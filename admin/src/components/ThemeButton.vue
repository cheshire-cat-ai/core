<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useSettings } from '@stores/useSettings'
import { storeToRefs } from 'pinia'

const settings = useSettings()
const { currentTheme } = storeToRefs(settings)
const isDark = ref(false)

const setTheme = (dark: boolean) => {
	const theme = dark ? 'dark' : 'light'
	currentTheme.value = theme
	document.documentElement.setAttribute('data-theme', theme)
	localStorage.setItem('theme', theme)
}

onMounted(() => {
	isDark.value = localStorage.getItem("theme") === 'dark' ||
		(!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
	setTheme(isDark.value)
})
</script>

<template>
	<button class="swap btn-ghost btn-square btn md:btn-sm" @click="setTheme(isDark = !isDark)">
		<input v-model="isDark" type="checkbox" class="modal-toggle">
		<heroicons-sun-solid class="swap-on h-6 w-6" />
		<heroicons-moon-solid class="swap-off h-6 w-6" />
	</button>
</template>
