/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly CORE_HOST: string
    readonly CORE_PORT: string
    readonly CORE_USE_SECURE_PROTOCOLS: boolean
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}