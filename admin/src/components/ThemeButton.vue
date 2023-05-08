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
	<button class="btn md:btn-sm btn-ghost btn-square swap" @click="setTheme(isDark = !isDark)">
		<input type="checkbox" class="modal-toggle" v-model="isDark" />
		<heroicons-sun-solid class="w-6 h-6 swap-on" />
		<heroicons-moon-solid class="w-6 h-6 swap-off" />
	</button>
</template>
