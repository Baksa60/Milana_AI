"""
Версия проекта Milana AI Bot
"""

# Версия всего проекта
PROJECT_VERSION = "1.0.0"

# Версии модулей
MODULES_VERSIONS = {
    "core": "1.0.0",
    "habits": "0.3.0",  # MVP в разработке
    "statistics": "0.6.0",  # MVP готов
    "horoscope": "0.0.0",  # Запланировано
    "subscriptions": "0.0.0",  # Запланировано
    "news": "0.0.0",  # Запланировано
    "settings": "0.0.0",  # Запланировано
}

def get_version(module: str = None) -> str:
    """Получить версию проекта или модуля"""
    if module:
        return MODULES_VERSIONS.get(module, "0.0.0")
    return PROJECT_VERSION

def get_full_version() -> str:
    """Получить полную версию с модулями"""
    modules_info = []
    for module, version in MODULES_VERSIONS.items():
        status = "✅" if version != "0.0.0" else "📋"
        modules_info.append(f"{status} {module}: {version}")
    
    return f"Milana AI v{PROJECT_VERSION}\n" + "\n".join(modules_info)

if __name__ == "__main__":
    print(get_full_version())
