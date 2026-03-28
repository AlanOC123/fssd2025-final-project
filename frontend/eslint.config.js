import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import prettier from 'eslint-config-prettier'
import { defineConfig, globalIgnores } from 'eslint/config'

/**
 * @fileoverview ESLint flat configuration for a React and TypeScript project.
 * Integrates recommended rules from ESLint, TypeScript-ESLint, and React Hooks,
 * while ensuring compatibility with Prettier and Vite.
 */

export default defineConfig([
    /**
     * Globally ignored paths that should not be processed by ESLint.
     */
    globalIgnores(['dist', 'src/routeTree.gen.ts']),

    {
        /** * Target TypeScript and React TSX files.
         */
        files: ['**/*.{ts,tsx}'],
        extends: [
            js.configs.recommended,
            tseslint.configs.recommended,
            reactHooks.configs.flat.recommended,
            reactRefresh.configs.vite,
            prettier,
        ],
        languageOptions: {
            ecmaVersion: 2020,
            globals: globals.browser,
        },
        rules: {
            'no-duplicate-imports': 'error',
            '@typescript-eslint/no-explicit-any': 'warn',

            /**
             * Enforce the use of 'import type' for type-only imports to improve
             * build performance and avoid side-effect imports.
             */
            '@typescript-eslint/consistent-type-imports': [
                'error',
                { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
            ],

            'react-hooks/exhaustive-deps': ['warn', { allowConstantExport: true }],

            /**
             * Prevent unintended console logs from reaching production,
             * while allowing necessary warning and error reporting.
             */
            'no-console': ['warn', { allow: ['warn', 'error'] }],
            'prefer-const': 'error',
        },
    },
])
