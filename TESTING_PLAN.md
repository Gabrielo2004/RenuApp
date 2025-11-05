 ## Plan de Pruebas – Renü App (Python + Kivy/KivyMD)

 Tabla de casos de prueba propuestos. Tipos: U (Unitaria), I (Integración), F (Funcional).

 | ID | Módulo | Descripción | Datos de entrada | Resultado esperado | Tipo |
 |---|---|---|---|---|---|
 | TST01 | Login | Validar ingreso con credenciales correctas | usuario="user1"; clave="secret123" | Cambia a pantalla "home" y mensaje "Bienvenido" | F |
 | TST02 | Login | Mostrar error con credenciales inválidas | usuario="user1"; clave="err" | Mensaje "Usuario o contraseña incorrectos" | F |
 | TST03 | Registro | Verificar error con usuario duplicado | usuario="nuevo" ya existente | Mensaje "El usuario ya existe" | U |
 | TST04 | Registro | Validar longitud mínima de contraseña | clave="123" | Mensaje "al menos 6 caracteres" | U |
 | TST05 | UsersRepository | Persistencia de sesión (set/get/clear) | user_id=42 | get=42; luego None tras clear | U |
 | TST06 | UsersRepository | Autenticación con hash y salt | alta de usuario + login | authenticate retorna id con clave válida | U |
 | TST07 | ChallengesRepository | Incremento de progreso semanal | challenge_id semanal | progreso aumenta en +2 | I |
 | TST08 | PointsRepository | Filtrado por material | filtro=["Papel"] | todos los puntos devueltos soportan algún material del filtro | I |
 | TST09 | Seed | Sincronización de tips con imágenes ausentes | sin imágenes en assets/images | no errores; no inserciones inesperadas | U |
 | TST10 | Navegación básica | Ocultar barra en auth y mostrar en home | estado login/logout | barra oculta en login, visible en home | F (manual/UI) |

 Notas:
 - Las pruebas F (funcionales) sobre UI se validan en lo posible con mocks y verificaciones indirectas; los flujos visuales completos pueden requerir validación manual.
 - Las pruebas I (integración) usan SQLite real en archivos temporales y los seeders del proyecto.


