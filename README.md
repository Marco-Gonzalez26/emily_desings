# Emily Designs - Sistema de E-commerce con IA

Sistema de recomendación inteligente para tienda de moda online con análisis
morfológico mediante inteligencia artificial.

## Descripción

Emily Designs es una plataforma de e-commerce desarrollada para mejorar la
experiencia de compra de ropa online. El sistema utiliza inteligencia artificial
para analizar la morfología corporal de los usuarios y recomendar prendas que
mejor se adapten a sus características físicas y preferencias personales.

##  Autores

- **Doris López** - Diseñadora e Investigadora
- **Emily Chiribora** - Diseñadora e Investigadora
- **Marco González** - Desarrollador

## Tecnologías

### Frontend

- **Framework**: Angular
- **Estilos**: CSS/Tailwind
- **Animaciones**: GSAP
- **Hosting**: Vercel

### Backend

- **Runtime**: Python con FastAPI
- **Base de Datos**: PostgreSQL
- **Hosting**: Render/Railway

### Inteligencia Artificial

- **Análisis Morfológico**: Modelo de IA personalizado
- **Sistema de Recomendación**: Filtrado colaborativo y basado en contenido
- **Entrenamiento**: Python con bibliotecas de Machine Learning

### Servicios Adicionales

- **Almacenamiento de Imágenes**: Cloudinary
- **Pasarela de Pagos**: Stripe
- **Autenticación**: JWT

## Características Principales

- Análisis morfológico mediante IA
- Recomendación personalizada de prendas
- Carrito de compras completo
- Sistema de pagos integrado
- Diseño responsive
- Gestión de perfiles de usuario
- Panel de administración

## Instalación

### Prerrequisitos

- Node.js v18+
- PostgreSQL 14+
- Python 3.8+
- npm o yarn

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
ng serve
```

## 📁 Estructura del Proyecto

```
emily-designs/
├── frontend/          # Aplicación Angular
├── backend/           # API REST con FastAPI
```

## TODO LIST

- [x] Crear la estructura de la aplicación
- [x] Crear la página de inicio

- [x] Implementar autenticación con JWT
- [x] Utiliza NG-ICONS para los iconos de la aplicación
- [x] Moficar la página de análisis morfológico para utilizar el Backend

