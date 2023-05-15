/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  extends: [
    './.eslintrc-auto-import.json',
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    "plugin:@typescript-eslint/recommended",
    "plugin:tailwindcss/recommended",
    "@vue/typescript/recommended",
    'plugin:vue/vue3-essential',
    '@vue/eslint-config-typescript'
  ],
  parser: "vue-eslint-parser",
  parserOptions: {
    ecmaVersion: 'latest',
    parser: "@typescript-eslint/parser",
  },
  rules: {
    "@typescript-eslint/consistent-type-imports": "warn",
    "no-empty-function": "off",
    "@typescript-eslint/no-empty-function": "warn",
    "vue/multi-word-component-names": "off",
    "vue/max-attributes-per-line": "off",
    "vue/first-attribute-linebreak": "off",
    "vue/html-indent": ["error", "tab", {
        "attribute": 1,
        "baseIndent": 1,
        "closeBracket": 0,
        "alignAttributesVertically": true,
        "ignores": []
    }],
    "vue/html-closing-bracket-newline": ["warn", {
        "singleline": "never",
        "multiline": "never"
    }],
    "vue/v-on-event-hyphenation": "off",
    "vue/attribute-hyphenation": "off",
    "tailwindcss/no-custom-classname": "off",
  }
}
