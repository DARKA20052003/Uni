#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")"

usage() {
    echo "Uso: $0 [estudiantes|inventario]"
    exit 1
}

[[ $# -ge 1 ]] || usage

case $1 in
    estudiantes)
        echo "Ejecutando app Estudiantes..."
        python3 -m Ejercicio1.ui.app_estudiantes
    ;;

    inventario)
        echo "Ejecutando app Inventario..."
        python3 -m Ejercicio2.ui.inventario_ui
    ;;

    *)
        usage
        ;;
esac