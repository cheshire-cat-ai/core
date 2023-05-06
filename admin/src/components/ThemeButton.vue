<template>
	<button class="btn md:btn-sm btn-ghost btn-square" title="Change theme" data-toggle-theme="dark,light" @click="setTheme(isDark = !isDark)">
		<div class="indicator mt-0.5">
			<span class="sr-only">Change theme mode</span>
			<Icon v-if="!isDark" :icon="moonIcon" class="w-6 h-6" aria-hidden="true" />
			<Icon v-else :icon="sunIcon" class="w-6 h-6" aria-hidden="true" />
		</div>
	</button>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue/dist/offline'
import sunIcon from '@iconify-icons/heroicons/sun-solid'
import moonIcon from '@iconify-icons/heroicons/moon-solid'
import { onMounted, ref } from 'vue'
import { useSettings } from '@stores/useSettings'
import { storeToRefs } from 'pinia'

const settings = useSettings()
const { currentTheme } = storeToRefs(settings)
const isDark = ref(false)

function setTheme(dark: boolean) {
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