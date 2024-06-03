# Módulo para Odoo v17 para extraer datos de Github y crear PDF y CSV a partir de ellos.
### Creado por Juan Pinilla

El objetivo del módulo en Odoo permite registrar y gestionar informació relacionada con los repositorios de código fuente de los clientes. El módulo incluye funcionalidades de visualizadión como administración de datos, enfocado en los detalles de los repositorios y los commit realizados.

*Para el funcionamiento del modulo debemos contar con Odoo versión 17.*

### Previo a el siguiente paso a paso de funcionamiento, el módulo debe estar incluido en la carpeta de addons (o carpeta asociada en la ruta de odoo.conf) del servidor, ya que si no esta presente en dicha carpeta, el modulo no se encontrará para la instalación.

## Instalación y permisos según rol

Como primer paso ingresamos como usuario tipo administrador:

(./images/home.png)

Procedemos a realizar la instalción del modulo ingresando a las aplicaciones y realizando la busqueda del modulo *"custom_repository"* en el buscador de la aplicaciones

(./images/Apps.png)

Despues de haber istalado el modulo, ingresamos a la sección de *Ajustes*

(./images/drop-down-configurations.png)

Buscamos en la parte superior *Usuarios y compañias* e ingresamos a *Usuarios*

(./images/Users-companies.png)

En el ejemplo tenemos creados dos usuarios:

- Usuario *"Admin"* que en este caso ejercera el rol de Administrador
- Usuario *"User"* que en este caso ejercera el rol de Usuario

(./images/Users.png)

Para tener acceso a el modulo *"custom_repository"* tanto como `admin` o `user` debemos otorgarle permismos

* Para el admin se otorgan permisos de *"Commit Administrator"*

(./images/admin-permissions.png)

* Para el user se otorgan permisos de *"Commit User"*

(./images/user-permissions.png)

## Funcionamiento del módulo

Ingresamos al módulo *"Github API"* desde el panel desplegable 

(./images/enter-module.png)

Y creamos un nuevo registro

(./images/new-search.png)

Nos mostrará una nueva ventana donde debemos ingresar datos importantes como *Github User Name* y *Github Token*

(./images/create-search.png)

### Si no ingresamos ningún dato nos mostrará el siguiente error

(./images/no-data.png)

### Si ingresamos algún dato incorrecto con los cuales no tenemos resultados en la busqueda obtenemos el siguiente error

(./images/incorrect-data.png)

### Dado el caso sea necesario, no se tenga conocimiento como crear un Github Token, el módulo cuenta con un botón que redirije a la documentación oficial de Github para generar el Token

(./images/press-help-token.png)

### *Cuando realizamos una busqueda con los datos correctamente, creamos un registro en el modelo **`res.partner`** con información básica del usuario y una tabla que adquiere los datos y repositorios asociados al cliente*

(./images/contacts.png)
(./images/contact_created.png)
(./images/repositories_from_contact.png)

En el módulo también tendremos acceso a la lista de repositorios

(./images/load-info-table.png)

Si ingresamos a algún registro de dicha lista, encontraremos una nueva ventana con 3 botones:

(./images/before-fetch.png)

- [Fetch Github Commit](#Busqueda de commits realizados)

### Si los commits fueron realizados hace menos de 24 horas es de color verde
(./images/after-fetch.png)

### Si los commits fueron realizados hace más de 24 horas es de color azul
(./images/fetch-time-ago.png)

- [Gereate Commit Report](#Creación de reporte en formato PDF de commits realizados)

(./images/pdf_report.png)

- [Gereate Commit Report](#Creación de reporte en formato CSV de commits realizados)

(./images/csv_report.png)

## Cuando se inicie sesión como *USER*

Se podrá tener acceso a la información pero no podrá ejecutar acciones diferentes a la creación de reporte en formato CSV

(./images/user-create-view.png)
(./images/user-fetch-view.png)
(./images/user-commit-view.png)

