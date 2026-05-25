"""
NIVEL 5: Incident CLI (Argparse)

Los scripts que requieren editar el código para cambiar una variable (ej. `ENV="prod"`)
son peligrosos en un incidente. Un buen SRE provee CLIs con `--help`.

Bridgewater Angle: Leverage. Si creas un CLI amigable, otro SRE Jr. o dev
puede resolver el problema sin despertarte a las 3 AM.
"""

import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def restart_service(service_name: str, env: str, force: bool):
    logger.info(f"Conectando al entorno: {env.upper()}...")
    
    if force:
        logger.warning(f"⚠️ FORCE = TRUE: Ignorando chequeos de salud previos. Matando {service_name}...")
    else:
        logger.info(f"Drenando tráfico amablemente de {service_name}...")
        
    logger.info(f"✅ Servicio {service_name} reiniciado con éxito en {env}.")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="🛠️ Internal SRE Incident CLI - Bridgewater Style",
        epilog="Recuerda: Si es prod, avisa en Slack #sre-alerts antes de ejecutar."
    )
    
    # Argumento posicional (Obligatorio)
    parser.add_argument("service", type=str, help="Nombre del microservicio a reiniciar (ej. auth-svc)")
    
    # Opciones (Flags)
    parser.add_argument("-e", "--env", type=str, choices=["dev", "staging", "prod"], default="dev",
                        help="Entorno objetivo (defecto: dev)")
                        
    parser.add_argument("-f", "--force", action="store_true",
                        help="Fuerza el reinicio sin Draining (Útil para emergencias/Outages)")
                        
    return parser

if __name__ == "__main__":
    # En la terminal pruébalo así:
    # python 02_incident_cli.py --help
    # python 02_incident_cli.py payment-svc --env prod --force
    
    parser = build_parser()
    
    # Si no pasan argumentos, imprimimos el help y salimos.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.env == "prod" and not args.force:
        logger.warning("Estás a punto de operar en PROD. Te recomendamos usar --force solo en P1s.")
        
    restart_service(args.service, args.env, args.force)
