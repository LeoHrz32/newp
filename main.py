from fastapi import FastAPI, File, Form, HTTPException, Header, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

# Inicializar la API
app = FastAPI()

# Diccionario con usuarios y contraseñas
users={
    "admin1": {"password": "admin1", "role": "admin"},
    "admin2": {"password": "admin2", "role": "viewer_downloader"},
    "admin3": {"password": "admin3", "role": "viewer"}
}

# Montar la carpeta estática para que FastAPI reconozca los archivos de estilo CSS
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/static")), name="static")

# Montar la carpeta 'CarpetaInfo' como una carpeta estática para acceder a los archivos PDF
app.mount("/CarpetaInfo", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../CarpetaInfo")), name="CarpetaInfo")

# Cargar la página de inicio de sesión
@app.get("/", response_class=HTMLResponse)
async def index():
    # Ruta del archivo HTML de inicio
    index_path = os.path.join(os.path.dirname(__file__), "../frontend/inicio.html")
    with open(index_path, "r", encoding="utf-8") as f:
        # Retornamos la respuesta en HTML
        return HTMLResponse(content=f.read(), status_code=200)

# Manejo del inicio de sesión
@app.post("/login")
async def login(strUsuario: str = Form(...), strContrasenna: str = Form(...)):
    # Verificar que el usuario exista y que la contraseña sea correcta
    if strUsuario in users and users[strUsuario]["password"] == strContrasenna:
        # Si la validación es correcta, redirigir según el rol
        if users[strUsuario]["role"] == "admin":
            # Redirigir a la página de admin con un método GET
            return RedirectResponse(url="/admin", status_code=303)  # 303 See Other (GET)
        elif users[strUsuario]["role"] == "viewer_downloader":
            # Redirigir a la página del viewerDownloader con un método GET
            return RedirectResponse(url="/viewer_downloader", status_code=303)  # 303 See Other (GET)
        else:
            # Redirigir a la página del viewer con un método GET
            return RedirectResponse(url="/viewer",status_code=303)
    else:
        # Si la validación falla, lanzar un error 401
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# Vista para permisos de administrador
@app.get("/admin")
async def view_admin():
    # Cargar la página HTML para el administrador
    admin_page_path = os.path.join(os.path.dirname(__file__), "../frontend/viewAdmin.html")
    with open(admin_page_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)
    
# Vista para permisos de visualización y descarga
@app.get("/viewer_downloader")
async def view_viewer_download():
    #Cargar la página HTML para descargar y ver el pdf
    viewer_download_page_path = os.path.join(os.path.dirname(__file__), "../frontend/viewViewerDownloader.html")
    with open(viewer_download_page_path,"r",encoding="utf-8") as f:
        return HTMLResponse(content=f.read(),status_code=200)

# Vista para permisos de visualización
@app.get("/viewer")
async def view_viewer():
    # Cargar la página HTML para el viewer
    viewer_page_path = os.path.join(os.path.dirname(__file__), "../frontend/viewViewer.html")
    with open(viewer_page_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

    
# Ruta para eliminar archivos de la carpeta (rol de admin)
@app.delete("/files/{filename}")
async def delete_file(filename: str):
    folder_path = os.path.join(os.path.dirname(__file__), "../CarpetaInfo")
    file_path = os.path.join(folder_path, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"Archivo '{filename}' eliminado correctamente."}
    else:
        raise HTTPException(status_code=404, detail="No se encontró el archivo a eliminar.")


# Endpoint para obtener los archivos PDF
@app.get("/api/get-files")
async def get_files():
    try:
        # Ruta a la carpeta donde están los archivos PDF
        folder_path = os.path.join(os.path.dirname(__file__), "../CarpetaInfo")
        
        # Verificar si la carpeta existe
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")
        
        # Obtener lista de archivos de la carpeta
        files = os.listdir(folder_path)
        
        # Filtrar solo los archivos .pdf
        pdf_files = [file for file in files if file.endswith(".pdf")]
        
        # Si no hay archivos PDF
        if not pdf_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos PDF")
        
        # Retornar los nombres de los archivos PDF
        return JSONResponse(content={"files": pdf_files})
    
    except Exception as e:
        # En caso de error, mostrar un mensaje adecuado
        raise HTTPException(status_code=500, detail=str(e))

# Vista de la carpeta con PDFs
# @app.get("/verdocumentos", response_class=HTMLResponse)
# async def ver_carpeta():
#     ver_carpeta_path = os.path.join(os.path.dirname(__file__), "../frontend/viewAdmin.html")
#     with open(ver_carpeta_path, "r", encoding="utf-8") as f:
#         return HTMLResponse(content=f.read(), status_code=200)

@app.get("/verdocumentos", response_class=HTMLResponse)
async def ver_carpeta(request: Request):
    user_role = request.headers.get("role")
    print(f"Rol recibido en /verdocumentos: {user_role}")  # Esto imprimirá el valor del rol recibido

    if user_role == "admin":
        view_path = os.path.join(os.path.dirname(__file__), "../frontend/viewAdmin.html")
    elif user_role == "viewer_downloader":
        view_path = os.path.join(os.path.dirname(__file__), "../frontend/viewViewerDownloader.html")
    elif user_role == "viewer":
        view_path = os.path.join(os.path.dirname(__file__), "../frontend/viewViewer.html")
    else:
        raise HTTPException(status_code=403, detail="Rol no válido o no autorizado")
    
    with open(view_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


    
    # # Leer y retornar el archivo HTML correspondiente
    # with open(view_path, "r", encoding="utf-8") as f:
    #     return HTMLResponse(content=f.read(), status_code=200)

# Ruta para manejar el logout y redirigir al login
@app.post("/logout")
async def logout(response: Response):
    # Eliminar la cookie de sesión
    response.delete_cookie("session") 
    
    # Redirigir al login
    return RedirectResponse(url="/", status_code=303)

# Ruta para subir archivos (rol de admin)
@app.post("/files/upload")
async def upload_file(request: Request, file: UploadFile= File(...)):
    # user_role = request.headers.get("Role")
    # if user_role != 'admin':
    #     raise HTTPException(status_code=403, detail="No tienes permisos para subir archivos.")
    
    folder_path = os.path.join(os.path.dirname(__file__),"../CarpetaInfo")
    file_path = os.path.join(folder_path, file.filename)
    
    with open(file_path,"wb") as f:
        f.write(await file.read())
    return{"message": f"Archivo '{file.filename}' subido correctamente a la carpeta."}


# Ruta para descargar archivos y visualizar (admin y viewer_downloader)
@app.get("/files/{file_name}")
async def download_file(file_name:str, request: Request):
    user_role = request.headers.get("Role")
    if user_role not in ["admin", "viewer_downloader"]:
        raise HTTPException(status_code=403, detail="Solo tienes permisos de visualización.")
    
    folder_path = os.path.join(os.path.dirname(__file__), "../CarpetaInfo")
    file_path = os.path.join(folder_path, file_name)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=file_name)
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")


    
    
