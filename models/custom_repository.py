from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo import http
from odoo.http import request
import requests
import base64
from datetime import datetime
import csv
import io
import json
from git import Repo

class CustomerRepository(models.Model):
    _name = 'customer.repository'
    _description = 'Customer Repository'

    #Create varibles to recollect data

    name = fields.Char(string='Github User Name')
    client_id = fields.Many2one('res.partner', string='Client')
    info_ids = fields.One2many('repository.info', 'info_id', string='Info')
    github_token = fields.Char(string='GitHub Token')

    def github_info(self):
        url = "https://docs.github.com/es/enterprise-server@3.9/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def fetch_github_info(self):
        for repository in self.search([]):
            if repository.name and repository.github_token:
                user_url = f'https://api.github.com/users/{repository.name}'
                headers = {
                            'Authorization': f'Bearer {repository.github_token}',
                            'X-GitHub-Api-Version': '2022-11-28'
                            }
                response = requests.get(user_url, headers=headers)
                if response.status_code == 200:
                    user_info = response.json()

                    # Obtain a partner photo

                    image_url = user_info['avatar_url']
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                    else:
                        image_base64 = False

                    # Search if partner exist
                    partner = self.env['res.partner'].search([('website', '=', user_info['html_url'])], limit=1)

                    # If exist, update, else, create
                    if partner:
                        partner.write({
                            'image_1920': image_base64,
                            'email': user_info.get('email'),
                            'website': user_info['html_url']
                        })
                    else:
                        partner = self.env['res.partner'].create({
                            'name': user_info['name'],
                            'image_1920': image_base64,
                            'email': user_info.get('email'),
                            'website': user_info['html_url']
                        })
                    
                    #Assign partner to variable
                    repository.client_id = partner.id

                    #Fetch the repos and load the table
                    repos_url = f'https://api.github.com/users/{repository.name}/repos'
                    response_repos = requests.get(repos_url, headers=headers)
                    if response_repos.status_code == 200:
                        repos = response_repos.json()
                        for repo in repos:
                            repo_id = self.env['repository.info'].search([('repo_id', '=', repo['id'])], limit=1)
                           
                            # If exist, update, else, create
                            if repo_id:
                                repo_id.write({
                                    'info_id': repository.id,
                                    'repo_id': repo['id'],
                                    'repository_name': repo['name'],
                                    'description': repo['description'],
                                    'url': repo['html_url'],
                                    'author': repo['owner']['login'],
                                    'last_update': datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
                                    'status': not repo['archived'] and not repo['disabled']
                                })
                            else:
                                self.env['repository.info'].create({
                                    'info_id': repository.id,
                                    'repo_id': repo['id'],
                                    'repository_name': repo['name'],
                                    'description': repo['description'],
                                    'url': repo['html_url'],
                                    'author': repo['owner']['login'],
                                    'last_update': datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
                                    'status': not repo['archived'] and not repo['disabled']
                            })

                else:
                    raise UserError("Your credentials seem to be incorrect.")

            else:
                raise UserError("You must enter your Github User and Github Token to continue.")

class RepositoryInfo(models.Model):
    _name = 'repository.info'
    _description = 'Repository Information'

    #Create variables to repositorie's data
    info_id = fields.Many2one('customer.repository', string='Repository')
    repo_id = fields.Char(string='Identifier')
    repository_name = fields.Char(string='Repository name')
    url = fields.Char(string='Repository URL')
    last_update = fields.Datetime(string='Last update')
    status = fields.Boolean(string='Status')
    description = fields.Char(string='Description')
    author = fields.Char(string='Author')
    commit_ids = fields.One2many('repository.commit', 'repository_id', string='Commits')
    major_contributor = fields.Char(string='Major Contributor')
    csv_data = fields.Binary()


    def fetch_github_commit(self):
        list_authors = []
        repeats = {}
        if self.info_id.github_token:
            url = f'https://api.github.com/repos/{self.info_id.name}/{self.repository_name}/commits'
            headers = {
                            'Accept': 'application/vnd.github+json',
                            'Authorization': f'Bearer {self.info_id.github_token}',
                            'X-GitHub-Api-Version': '2022-11-28'
                            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                commits = response.json()
                for commit in commits:

                    #List the authors to know the contributors
                    list_authors.append(commit['commit']['author']['name'])

                    #If commit exist, don't create a new record
                    hash_rep = self.env['repository.commit'].search([('commit_hash','=',commit['sha'])])
                    if not hash_rep:
                        self.env['repository.commit'].create({
                            'repository_id': self.id,
                            'commit_hash': commit['sha'],
                            'author': commit['commit']['author']['name'],
                            'date': datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
                            'message': commit['commit']['message'],
                            'url_commit': commit['html_url']
                        })
                
                #Know the major contributor
                for n in list_authors:
                    if n in repeats:
                        repeats[n] += 1
                    else:
                        repeats[n] = 1

                self.major_contributor = f"The major contribuitor is {max(list_authors, key=repeats.get)} with {repeats[max(list_authors, key=repeats.get)]} commits"

    #Obtain the URL of the last commit
    def link_to_last_commit(self):
        url = f'https://api.github.com/repos/{self.info_id.name}/{self.repository_name}/commits'
        headers = {
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {self.info_id.github_token}',
                    'X-GitHub-Api-Version': '2022-11-28'
                  }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            if commits:
                last_commit_url = commits[0]['html_url']
                return {
                    'type': 'ir.actions.act_url',
                    'url': last_commit_url,
                    'target': 'new',
                }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'repository.commit',
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }
    
    def create_csv(self):
        csv_content = 'commit_hash,author,date,message\n'
        for commit in self.commit_ids:
            csv_content += f'{commit.commit_hash},{commit.author},{commit.date},{commit.message}\n'
        print(csv_content)

        self.csv_data = base64.b64encode(csv_content.encode('utf-8'))
        filename = 'repository_commits.csv'

        print("CSV Data Length:", len(self.csv_data))
        print("Filename:", filename)

        # Return action to download the CSV file
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=repository.info&id=" + str(self.id) +
                "&filename=repository_commits.csv&field=csv_data&download=true&filename=" + filename,
            'target': 'self',
        }


class RepositoryCommit(models.Model):
    _name = 'repository.commit'
    _description = 'Repository Commit'

    #Variables to commit info
    repository_id = fields.Many2one('repository.info', string='Repository', required=True)
    commit_hash = fields.Char(string='Commit Hash', required=True)
    author = fields.Char(string='Author', required=True)
    date = fields.Datetime(string='Date', required=True)
    message = fields.Text(string='Message', required=True)
    url_commit = fields.Char()
    time_elapsed = fields.Char(string='Time Elapsed', compute='_compute_time_elapsed')

    #Variable for paint the confirmation according to the time elapsed
    color = fields.Boolean(string='Color', compute='_compute_time_elapsed')

    #Calculation of  the time elapsed since the last update
    @api.depends('date')
    def _compute_time_elapsed(self):
        for record in self:
            if record.date:
                current_time = datetime.now()
                commit_time = fields.Datetime.from_string(record.date)
                time_diff = current_time - commit_time

                days = time_diff.days
                seconds = time_diff.seconds
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60

                if days < 1:
                    time_elapsed_str = f"The last commit was {hours} hours"
                    record.color = True
                else:
                    time_elapsed_str = f"The last commit was {days} days"
                    record.color = False
                    

                record.time_elapsed = time_elapsed_str
            else:
                record.time_elapsed = "Date not set" 


class CustomerRepos(models.Model):
    _inherit = 'res.partner'
    _description = 'Model to relation the partner with repository'

    repos_ids = fields.One2many('customer.repository', 'client_id', string='Repositries')


