## FASE 7 -- Web Next.js (anonima)

### 7.1 Por que esta fase no tiene auth

La web del nucleo es **publica y anonima**. Sin `middleware.ts`, sin Server Action
de login, sin `getUser()` en el layout, sin cookies de sesion.

Es el mismo criterio que en mobile: un bootstrap que genera un login te resuelve
una pregunta que el proyecto todavia no se hizo. Si tu web necesita usuarios, el
`## PACK: auth` agrega el `middleware.ts` y las Server Actions.

El nucleo si demuestra el patron correcto de Next.js + Supabase, que es el que
importa: **cliente para el navegador, servidor para render y para datos.**

### 7.2 Estructura

```
apps/web/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   └── error.tsx
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   └── server.ts
│   └── utils.ts
├── components/
│   └── ui/
│       └── card.tsx
├── public/
├── .env.example
├── .env.local
├── eslint.config.mjs
├── next.config.ts
├── package.json
├── package-lock.json
├── postcss.config.mjs
├── tsconfig.json
├── Makefile
└── README.md
```

**Sin `src/`.** Next.js usa el directorio raiz por defecto y agregar `src/` por
costumbre produce un `tsconfig` con dos roots y un alias que apunta al lugar
equivocado.

### 7.3 `package.json`

```json
{
  "name": "{{NOMBRE_PROYECTO}}-web",
  "version": "{{VERSION_INICIAL}}",
  "private": true,
  "engines": {
    "node": ">=20"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint --max-warnings=0",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "audit": "npm audit --audit-level=high"
  },
  "dependencies": {
    "@supabase/ssr": "^0.5.2",
    "@supabase/supabase-js": "^2.47.10",
    "next": "16.2.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.1.0",
    "@types/node": "^22.10.2",
    "@types/react": "^19.0.2",
    "@types/react-dom": "^19.0.2",
    "@vitejs/plugin-react": "^4.3.4",
    "eslint": "^9.17.0",
    "eslint-config-next": "16.2.6",
    "jsdom": "^25.0.1",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/postcss": "^4.0.0",
    "typescript": "^5.7.2",
    "vitest": "^2.1.8"
  }
}
```

> **Version exacta en `next` y `eslint-config-next`.** El rango `^16.2.6` en `next`
> deja que un minor rompa el build un martes. Next es estricto con las
> personalizaciones de webpack y las deprecaciones entre minors son reales. Fijalo
> y dejalo mover con Dependabot, que abre el PR.

> **Tailwind v4, CSS-first.** No hay `tailwind.config.js`. La configuracion vive en
> `globals.css` con `@theme`. Es la forma que la v4 proyecta, y agregar un
> `tailwind.config.ts` a un proyecto v4 es mezclar dos sistemas de configuracion.

### 7.4 `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

> **`@/*` apunta a la raiz, no a `./src/*`.** Sin `src/`, el alias es `./*`. Es
> menos elegante de escribir y evita el error de mover un archivo a `src/` y que
> el alias deje de resolver.

### 7.5 `next.config.ts`

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,

  // No filtrar `NEXT_PUBLIC_SUPABASE_*` en los logs del servidor: con
  // `poweredByHeader: false` y este filtro, el log no dice que backend estas
  // usando. El log de acceso va al servidor de observabilidad, no a la consola
  // del contenedor.
  logging: {
    fetches: { fullUrl: false },
  },

  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
        ],
      },
    ];
  },
};

export default nextConfig;
```

### 7.6 El patron Supabase: dos clientes

Este es el nucleo del patron y lo unico que hay que Internalizar de la capa web.

```typescript
// lib/supabase/client.ts
'use client';

import { createBrowserClient } from '@supabase/ssr';

/**
 * Cliente de Supabase para el navegador.
 *
 * El prefijo 'use client' es lo que lo convierte en un Client Component. Sin el,
 * Next lo trata como Server Component y tira al usar un hook.
 *
 * `createBrowserClient` **memoriza** el cliente en el scope del modulo. Por eso
 * `const supabase = createBrowserClient(...)` a nivel de archivo y no dentro del
 * componente: dentro del componente se crea uno nuevo en cada render, y cada uno
 * abre su propia conexion Realtime.
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
  );
}
```

```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

/**
 * Cliente de Supabase para el servidor.
 *
 * Las cookies se escriben en un Server Action o en un Route Handler, no durante
 * el render. Por eso `getAll`/`setAll` en vez de `get`/`set`: si Supabase refresca
 * el token durante el render, `setAll` lo tira y el render falla.
 */
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // En Server Components, `cookies().set` tira: son read-only. Es
            // esperado cuando el refresh del token ocurre durante el render.
            // El error se ignora a proposito, porque la sesion se va a refrescar
            // en el proximo Server Action. Un `throw` aca deja la pagina en
            // blanco.
          }
        },
      },
    },
  );
}
```

> **Por que dos archivos y no uno con una bandera:** el import de
> `createBrowserClient` arrastra codigo de navegador a un modulo que corre en
> Node. Separarlos hace que el error sea visible en el momento del import y no
> en el primer click.

### 7.7 `app/layout.tsx`, `page.tsx`, `globals.css`

```tsx
// app/layout.tsx
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '{{NOMBRE_MOSTRABLE}}',
  description: 'Descripcion del producto, en una linea.',
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
```

```tsx
// app/page.tsx
import { createClient } from '@/lib/supabase/server';

/**
 * Landing publica.
 *
 * `createClient()` sin sesion: es una pagina anonima y usa el rol `anon`, con las
 * policies RLS de lectura publica. Si la pagina necesita datos privados, ver
 * `## PACK: auth`.
 */
export default async function Home() {
  const supabase = await createClient();

  const { data, error } = await supabase.rpc('get_public_entries');

  if (error) {
    // El error va al log del servidor. Al visitante le llega la pagina sin datos,
    // no un stack trace con el nombre de la funcion SQL.
    console.error('Error cargando entradas publicas:', error.message);
  }

  const entries = data ?? [];

  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold">{{NOMBRE_MOSTRABLE}}</h1>
      <p className="mt-2 text-zinc-600">
        Descripcion del producto, en una linea.
      </p>

      <section className="mt-12">
        <h2 className="text-xl font-semibold">Entradas publicas</h2>

        {entries.length === 0 ? (
          <p className="mt-4 text-zinc-500">
            Todavia no hay nada. Corré `supabase db reset` con datos de semilla.
          </p>
        ) : (
          <ul className="mt-4 space-y-2">
            {entries.map((entry) => (
              <li
                key={entry.id}
                className="rounded-lg border border-zinc-200 p-4"
              >
                {entry.title}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
```

> **La RPC `get_public_entries` no existe todavia.** El nucleo no genera schema de
> negocio. Para que la web compile y renderice, generá esta migration minima en
> `supabase/migrations/00001_public_entries.sql`:
>
> ```sql
> -- Entradas publicas de lectura.
> create table if not exists public.public_entries (
>   id uuid primary key default gen_random_uuid(),
>   title text not null,
>   created_at timestamptz not null default now()
> );
>
> alter table public.public_entries enable row level security;
>
> -- RLS habilitado y sin policies = denegar todo. Vamos a agregar la de lectura.
> create policy "Anyone can read public entries"
>   on public.public_entries for select
>   to anon, authenticated
>   using (true);
>
> -- RPC de lectura. security definer con search_path acotado: sin esto, un
> -- atacante con CREATE en el schema puede ejecutar su codigo dentro de la
> -- funcion con los permisos de la funcion. Ver supabase/migrations/README.md.
> create or replace function public.get_public_entries()
> returns setof public.public_entries
> language sql
> security definer
>   set search_path = ''
> as $$
>   select * from public.public_entries order by created_at desc;
> $$;
>
> revoke execute on function public.get_public_entries() from public;
> grant execute on function public.get_public_entries() to anon, authenticated;
> ```
>
> **Sobre `using (true)`:** esta es **una de las dos** unicas lugares del bootstrap
> donde la lectura anonima es abierta. Es correcto para contenido que es publico
> por definicion, y por eso el nombre de la policy dice `public_entries` y no
> algo con datos personales. Si tu tabla tiene datos de terceros, la policy va
> con filtro. Ver `## PACK: rpc-publicas`.
>
> Agrega el test pgTAP correspondiente en `supabase/tests/002_public_entries_test.sql`:
> que el `anon` lee, que el `authenticated` lee, y que un `service_role` puede
> escribir mientras el `anon` no.

```css
/* app/globals.css */
@import 'tailwindcss';

@theme {
  /* Tailwind v4 es CSS-first: los tokens se definen aca, no en un
     tailwind.config.js. `--color-*` genera las utilidades `bg-*`, `text-*`,
     etc. automaticamente. */
  --color-brand-50: oklch(0.97 0.02 260);
  --color-brand-500: oklch(0.62 0.19 260);
  --color-brand-600: oklch(0.55 0.20 260);
  --color-brand-900: oklch(0.28 0.09 260);
}

/* Reset minimo. Tailwind v4 ya trae su preflight. */
@layer base {
  body {
    @apply bg-white text-zinc-900 antialiased;
  }
}
```

```tsx
// app/error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="mx-auto max-w-2xl px-4 py-24 text-center">
      <h1 className="text-2xl font-bold">Algo salio mal</h1>
      <p className="mt-3 text-zinc-600">
        Vimos el problema. Proba de nuevo.
      </p>

      {/* El digest corre en produccion y sirve para buscar el error en el
          servidor de observabilidad. Es lo unico del error que se puede mostrar. */}
      {error.digest && (
        <p className="mt-2 font-mono text-xs text-zinc-400">
          Referencia: {error.digest}
        </p>
      )}

      <button
        onClick={reset}
        className="mt-6 rounded-lg bg-brand-600 px-4 py-2 text-white"
      >
        Reintentar
      </button>
    </main>
  );
}
```

### 7.8 `lib/utils.ts`, `components/ui/card.tsx`

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';

/** Concatena clases condicionales. `clsx` se llama `cva` en algunos proyectos. */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
```

> Este archivo necesita la dependencia `clsx`. Agregala al `package.json` de la
> web en el bloque de dependencias:
>
> ```json
> "clsx": "^2.1.1",
> ```

```tsx
// components/ui/card.tsx
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export function Card({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'rounded-lg border border-zinc-200 bg-white p-4 shadow-sm',
        className,
      )}
    >
      {children}
    </div>
  );
}
```

### 7.9 `.env.example` y `.env.local` de la web

```bash
# Copiala a .env.local. NUNCA commitees .env.local.
#
# NEXT_PUBLIC_* se hornea en el bundle en tiempo de build: queda visible para
# cualquiera que abra las devtools. Es correcto para la publishable key.
# Lo que jamas va aca es la secret key.

NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_TU_CLAVE_PUBLISHABLE_AQUI
```

`.env.local` con los mismos valores de `supabase start`.

### 7.10 `eslint.config.mjs`, `postcss.config.mjs`, test de web

```javascript
// eslint.config.mjs
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat({
  baseDirectory: dirname(fileURLToPath(import.meta.url)),
});

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  },
];
```

```javascript
// postcss.config.mjs
const config = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};

export default config;
```

```typescript
// vitest.config.ts
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./', import.meta.url)),
    },
  },
});
```

```typescript
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
```

```tsx
// components/ui/card.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Card } from '@/components/ui/card';

describe('Card', () => {
  it('renderiza sus hijos', () => {
    // ARRANGE & ACT
    render(
      <Card>
        <p>Contenido</p>
      </Card>,
    );

    // ASSERT
    expect(screen.getByText('Contenido')).toBeInTheDocument();
  });

  it('aplica las clases que le pasan', () => {
    // ARRANGE & ACT
    const { container } = render(
      <Card className="p-8">
        <p>Contenido</p>
      </Card>,
    );

    // ASSERT
    expect(container.firstChild).toHaveClass('p-8');
  });
});
```

### 7.11 `apps/web/Makefile` y `README.md`

```makefile
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

.PHONY: help
help: ## Muestra esta ayuda
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

.PHONY: install
install: ## Instala dependencias
	npm ci

.PHONY: dev
dev: ## Levanta el servidor de desarrollo
	npm run dev

.PHONY: build
build: ## Build de produccion
	npm run build

.PHONY: start
start: ## Sirve el build de produccion
	npm run start

.PHONY: lint
lint: ## ESLint
	npm run lint

.PHONY: typecheck
typecheck: ## Chequeo de tipos
	npm run typecheck

.PHONY: test
test: ## Tests unitarios
	npm run test

.PHONY: check
check: lint typecheck test ## lint + typecheck + test
	@echo "ok: web"

.PHONY: audit
audit: ## npm audit con nivel high
	npm run audit

.PHONY: env-local
env-local: ## Copia .env.example a .env.local
	@cp .env.example .env.local
	@$(MAKE) --no-print-directory env-check

.PHONY: env-check
env-check: ## Verifica que .env.local tenga valores
	@if grep -q 'TU_CLAVE_PUBLISHABLE_AQUI' .env.local 2>/dev/null; then \
		echo "FALLA: la publishable key sigue siendo el placeholder."; exit 1; \
	fi
	@echo "  ok    .env.local parece completo"

.PHONY: clean
clean: ## Borra .next y node_modules
	rm -rf .next node_modules
```

```markdown
# {{NOMBRE_PROYECTO}} (web)

## Requisitos

- Node 20+ (`nvm use`)
- Supabase local corriendo (ver `make db-up` en la raiz)

## Arranque

```bash
make install
make env-local
make dev        # http://localhost:{{PUERTO_WEB}}
```

## Estructura

```
app/          rutas del App Router. Un archivo por ruta.
lib/supabase/ los dos clientes. Ver abajo.
components/   componentes de UI sin logica de datos.
```

## El patron de Supabase

Dos clientes, y la diferencia es **cuando se ejecuta**:

| Archivo | Donde corre | Para que |
|---|---|---|
| `lib/supabase/client.ts` | Navegador (Client Component) | Eventos del usuario: formularios, Realtime |
| `lib/supabase/server.ts` | Node (Server Component, Action, Route Handler) | Render y lectura de datos |

Reglas:

1. `createClient()` de `server.ts` es `async` porque usa `cookies()`.
2. `createClient()` de `client.ts` se llama **a nivel de modulo**, no dentro del
   componente. Adentro se crea uno nuevo en cada render.
3. Las cookies se escriben solo desde Server Actions y Route Handlers, nunca
   durante el render.
4. `NEXT_PUBLIC_*` queda en el bundle. Jamas la secret key.

## Variables

| Variable | Donde | Visible |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | bundle | si |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | bundle | si |
| `SUPABASE_SERVICE_ROLE_KEY` | servidor | **no** |

La publishable key es publica por diseno: viaja en el bundle y lo unico que
protege son las policies RLS. La secret key saltea RLS y jamas va en el cliente.

## Pendientes

- [ ] **Auth en la web.** La web del bootstrap es publica. Si necesita sesiones,
      ver `## PACK: auth` en `PROMPT-POR-FASES/09-parte-b-packs.md`.
- [ ] **Deploy.** Configurar Vercel o el host que corresponda, con las
      variables de `NEXT_PUBLIC_*` en los settings del proyecto.
- [ ] **Dominio y HTTPS.** Configurar los redirect URLs de Auth si se agrega
      auth.
- [ ] **Imagenes y OG metadata.** `metadataBase` y `openGraph` para compartir
      links en redes.
```

> **VERIFICAR FASE 7**

```bash
cd apps/web
make install
cp .env.example .env.local
npm run lint
npm run typecheck
npm run test -- --run
npm run build
npm run start &
curl -s http://localhost:{{PUERTO_WEB}} | grep -q 'Entradas publicas' && echo "ok: la landing renderiza"
```

---

