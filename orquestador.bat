@echo off
echo ================================
echo Configurando entorno virtual y dependencias...
echo ================================

python -m venv .venv
call .venv\Scripts\activate

echo ================================
echo Instalando dependencias...
echo ================================

pip install -r requirements.txt -q
echo Dependencias instaladas correctamente.

echo ================================
echo Entorno listo para usar.
echo ================================
