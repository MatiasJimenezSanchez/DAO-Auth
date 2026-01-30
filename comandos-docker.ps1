# ============================================================================
# Comandos Docker para Aurum DAO API
# ============================================================================
# Uso: . .\comandos-docker.ps1  (cargar en sesión actual)
# ============================================================================

$Global:AURUM_PROJECT = "C:\Users\matji\OneDrive\Documentos\MATI\PROYECTOS\AURUM BACK END"

function aurum-start {
    <#
    .SYNOPSIS
    Inicia todos los servicios de Aurum DAO
    #>
    Write-Host "🚀 Iniciando Aurum DAO API..." -ForegroundColor Cyan
    Set-Location $Global:AURUM_PROJECT
    docker-compose up -d
    Start-Sleep -Seconds 5
    docker-compose ps
    Write-Host "`n✓ Servicios iniciados" -ForegroundColor Green
    Write-Host "📝 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
}

function aurum-stop {
    <#
    .SYNOPSIS
    Detiene todos los servicios de Aurum DAO
    #>
    Write-Host "⏸️  Deteniendo Aurum DAO API..." -ForegroundColor Yellow
    Set-Location $Global:AURUM_PROJECT
    docker-compose down
    Write-Host "✓ Servicios detenidos" -ForegroundColor Green
}

function aurum-restart {
    <#
    .SYNOPSIS
    Reinicia todos los servicios de Aurum DAO
    #>
    Write-Host "🔄 Reiniciando Aurum DAO API..." -ForegroundColor Cyan
    aurum-stop
    Start-Sleep -Seconds 2
    aurum-start
}

function aurum-logs {
    <#
    .SYNOPSIS
    Muestra logs de los servicios
    .PARAMETER Service
    Servicio específico (web o db). Si no se especifica, muestra todos.
    .PARAMETER Follow
    Seguir logs en tiempo real
    #>
    param(
        [string]$Service = "",
        [switch]$Follow
    )
    
    Set-Location $Global:AURUM_PROJECT
    
    if ($Follow) {
        if ($Service) {
            docker-compose logs -f $Service
        } else {
            docker-compose logs -f
        }
    } else {
        if ($Service) {
            docker-compose logs --tail=100 $Service
        } else {
            docker-compose logs --tail=100
        }
    }
}

function aurum-shell {
    <#
    .SYNOPSIS
    Abre un shell interactivo en el contenedor especificado
    .PARAMETER Service
    Servicio (web o db). Por defecto: web
    #>
    param(
        [string]$Service = "web"
    )
    
    Write-Host "🐚 Abriendo shell en contenedor: $Service" -ForegroundColor Cyan
    Set-Location $Global:AURUM_PROJECT
    
    if ($Service -eq "db") {
        docker-compose exec db psql -U postgres -d aurum_dao
    } else {
        docker-compose exec web /bin/bash
    }
}

function aurum-migrate {
    <#
    .SYNOPSIS
    Ejecuta migraciones de Alembic
    .PARAMETER Action
    Acción: upgrade, downgrade, revision, history
    .PARAMETER Target
    Target para upgrade/downgrade (por defecto: head)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("upgrade", "downgrade", "revision", "history", "current")]
        [string]$Action,
        [string]$Target = "head",
        [string]$Message = ""
    )
    
    Set-Location $Global:AURUM_PROJECT
    
    switch ($Action) {
        "upgrade" {
            Write-Host "⬆️  Aplicando migraciones..." -ForegroundColor Cyan
            docker-compose exec web alembic upgrade $Target
        }
        "downgrade" {
            Write-Host "⬇️  Revirtiendo migraciones..." -ForegroundColor Yellow
            docker-compose exec web alembic downgrade $Target
        }
        "revision" {
            if (-not $Message) {
                Write-Host "❌ Se requiere un mensaje para la revisión" -ForegroundColor Red
                return
            }
            Write-Host "📝 Creando nueva revisión..." -ForegroundColor Cyan
            docker-compose exec web alembic revision --autogenerate -m "$Message"
        }
        "history" {
            docker-compose exec web alembic history
        }
        "current" {
            docker-compose exec web alembic current
        }
    }
}

function aurum-test {
    <#
    .SYNOPSIS
    Ejecuta tests con pytest
    .PARAMETER Path
    Ruta específica de tests. Por defecto: todos
    #>
    param(
        [string]$Path = "tests/"
    )
    
    Write-Host "🧪 Ejecutando tests..." -ForegroundColor Cyan
    Set-Location $Global:AURUM_PROJECT
    docker-compose exec web pytest $Path -v
}

function aurum-rebuild {
    <#
    .SYNOPSIS
    Reconstruye las imágenes de Docker desde cero
    #>
    Write-Host "🔨 Reconstruyendo imágenes..." -ForegroundColor Cyan
    Set-Location $Global:AURUM_PROJECT
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    Write-Host "✓ Reconstrucción completada" -ForegroundColor Green
}

function aurum-status {
    <#
    .SYNOPSIS
    Muestra el estado de todos los servicios
    #>
    Write-Host "`n📊 Estado de Aurum DAO API" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Set-Location $Global:AURUM_PROJECT
    docker-compose ps
    Write-Host "`n📝 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
    Write-Host "🗄️  PostgreSQL: localhost:5432" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
}

function aurum-db-reset {
    <#
    .SYNOPSIS
    Reinicia completamente la base de datos (¡PELIGRO!)
    #>
    Write-Host "⚠️  ADVERTENCIA: Esto eliminará TODOS los datos" -ForegroundColor Red
    $confirm = Read-Host "¿Estás seguro? (escribe 'SI' para confirmar)"
    
    if ($confirm -eq "SI") {
        Write-Host "🗑️  Eliminando base de datos..." -ForegroundColor Yellow
        Set-Location $Global:AURUM_PROJECT
        docker-compose down -v
        docker-compose up -d db
        Start-Sleep -Seconds 5
        docker-compose up -d web
        Start-Sleep -Seconds 3
        Write-Host "🔄 Aplicando migraciones..." -ForegroundColor Cyan
        docker-compose exec web alembic upgrade head
        Write-Host "✓ Base de datos reiniciada" -ForegroundColor Green
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

function aurum-help {
    <#
    .SYNOPSIS
    Muestra ayuda de comandos disponibles
    #>
    Write-Host "`n🎯 Comandos disponibles para Aurum DAO API" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "  aurum-start         " -NoNewline; Write-Host "Inicia todos los servicios" -ForegroundColor Gray
    Write-Host "  aurum-stop          " -NoNewline; Write-Host "Detiene todos los servicios" -ForegroundColor Gray
    Write-Host "  aurum-restart       " -NoNewline; Write-Host "Reinicia todos los servicios" -ForegroundColor Gray
    Write-Host "  aurum-logs [srv]    " -NoNewline; Write-Host "Muestra logs (usa -Follow para seguir)" -ForegroundColor Gray
    Write-Host "  aurum-shell [srv]   " -NoNewline; Write-Host "Abre shell en contenedor (web o db)" -ForegroundColor Gray
    Write-Host "  aurum-migrate       " -NoNewline; Write-Host "Ejecuta migraciones de Alembic" -ForegroundColor Gray
    Write-Host "  aurum-test [path]   " -NoNewline; Write-Host "Ejecuta tests con pytest" -ForegroundColor Gray
    Write-Host "  aurum-rebuild       " -NoNewline; Write-Host "Reconstruye imágenes desde cero" -ForegroundColor Gray
    Write-Host "  aurum-status        " -NoNewline; Write-Host "Muestra estado de servicios" -ForegroundColor Gray
    Write-Host "  aurum-db-reset      " -NoNewline; Write-Host "Reinicia la base de datos (¡PELIGRO!)" -ForegroundColor Gray
    Write-Host "  aurum-help          " -NoNewline; Write-Host "Muestra esta ayuda" -ForegroundColor Gray
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
}

# Mensaje de bienvenida
Write-Host "✓ Comandos Aurum DAO cargados" -ForegroundColor Green
Write-Host "  Usa 'aurum-help' para ver todos los comandos disponibles" -ForegroundColor Gray
