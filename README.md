# Boutique Inmobiliaria (Django Backend)

Este es un proyecto backend desarrollado en **Django** con base de datos **MySQL**, enfocado en la gestión de un catálogo de bienes raíces. Permite el manejo completo (CRUD) del catálogo de propiedades a través de una interfaz estéticamente cuidada y provee autenticación tanto vía web como a través de una **API REST**.

## Tecnologías Utilizadas
* **Backend:** Django 5.0+, Python 3
* **Base de Datos:** MySQL / MariaDB (integrado vía `mysqlclient`)
* **API REST:** Django REST Framework (DRF) + Token Authentication
* **Frontend:** HTML5, CSS3, Bootstrap 5 (estilizado con enfoque minimalista y tipografía Montserrat)

## Alcance del Proyecto

1. **Gestión de Propiedades (CRUD Completo)**
   - **Crear, Leer, Actualizar y Eliminar (Baja Lógica):** Las propiedades no se borran definitivamente de la base de datos, sino que cambian su estado a "Inactiva/Eliminada" (Soft Delete).
   - **Administración de Estados:** Las propiedades pueden estar "Disponibles", "Reservadas" o "Vendidas".
   - **Filtros de Búsqueda:** Búsqueda avanzada por fecha de creación, rangos de precio y estado de venta.
   
2. **Autenticación de Usuarios (Web y API)**
   - **Sistema Web:** Formularios de inicio de sesión (`/login/`) para restringir el acceso a las funciones administrativas.
   - **API REST (`/api/auth/login/`):** Endpoint JSON para autenticar clientes externos que devuelve un *Token* de autorización.

3. **Robustez y Validaciones Estrictas**
   - **Restricciones Lógicas:** Topes máximos para valores numéricos (máximo 50 habitaciones, 20 baños, precios ajustados según tipo de moneda UF/CLP).
   - **Normalización y Límites:** El texto de descripción está limitado a un máximo de 800 caracteres. Existen filtros contra caracteres extraños y se restringe la sobrecarga de datos en usuario (max 150) y contraseña (max 128).
   - **Archivos:** Limite de peso en carga de fotografías (máximo 5MB).


## Futuras Implementaciones

Para seguir robusteciendo la plataforma, se han planificado las siguientes mejoras:

* **Limitación de Intentos de Contraseña (Rate Limiting):** Implementar un mecanismo (usando la Caché de Django o `django-axes`) para limitar los intentos fallidos de inicio de sesión a un máximo de 5 intentos. Al superar este límite, el sistema arrojará un mensaje que indicará al usuario que debe comunicarse con el administrador, previniendo así ataques de fuerza bruta.
