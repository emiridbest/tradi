import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

// Create the flat config with rules
const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Enforce using @ts-expect-error instead of @ts-ignore
      '@typescript-eslint/ban-ts-comment': [
        'error',
        {
          'ts-expect-error': 'allow-with-description',
          'ts-ignore': 'never',
          'ts-nocheck': 'never',
          'ts-check': 'never',
        },
      ],
      // Disallow explicit any type
      '@typescript-eslint/no-explicit-any': 'error',
      // Enforce hook dependencies
      'react-hooks/exhaustive-deps': 'warn',
    },
  }
];

export default eslintConfig;