<script setup lang="ts">
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import ThemeButton from '@components/ThemeButton.vue'
import { RouterLink } from 'vue-router'
import { Icon } from '@iconify/vue/dist/offline'
import menuIcon from '@iconify-icons/heroicons/bars-3-20-solid'
import markIcon from '@iconify-icons/heroicons/x-mark-solid'
</script>

<template>
  <div class="navbar md:px-[10%] bg-base-100 min-h-fit shadow-xl">
    <div class="navbar-start">
      <img src="@assets/logo.svg" class="hidden w-8 h-8 md:block" />
      <Menu v-slot="{ open }" as="div" class="relative inline-block rounded-lg md:hidden">
				<MenuButton class="btn-ghost btn-square btn" title="Menu">
					<Icon v-if="!open" :icon="menuIcon" class="w-6 h-6" aria-hidden="true" />
					<Icon v-else :icon="markIcon" class="w-6 h-6" aria-hidden="true" />
				</MenuButton>
				<Transition enter-active-class="transition duration-200 ease-out"
					enter-from-class="transform scale-90 opacity-0" enter-to-class="transform scale-100 opacity-100"
					leave-active-class="transition duration-200 ease-in"
					leave-from-class="transform scale-100 opacity-100" leave-to-class="transform scale-90 opacity-0">
					<MenuItems as="ul"
						class="absolute left-0 z-50 gap-2 p-2 mt-4 font-semibold origin-top-left shadow-xl whitespace-nowrap w-min menu menu-compact rounded-box bg-base-300">
						<MenuItem as="li">
							<RouterLink to="/">🏠️ Home</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<RouterLink to="/plugins">🔌 Plugins</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<RouterLink to="/settings">⚙️ Settings</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<a href="https://pieroit.github.io/cheshire-cat" target="_blank">📖 Documentation</a>
						</MenuItem>
					</MenuItems>
				</Transition>
			</Menu>
    </div>
    <div class="navbar-center">
      <img src="@assets/logo.svg" class="w-10 h-10 md:hidden" />
      <ul class="hidden gap-2 px-1 font-semibold menu menu-horizontal menu-compact md:flex">
        <li><RouterLink to="/">🏠️ Home</RouterLink></li>
        <li><RouterLink to="/plugins">🔌 Plugins</RouterLink></li>
        <li><RouterLink to="/settings">⚙️ Settings</RouterLink></li>
        <li><a href="https://pieroit.github.io/cheshire-cat" target="_blank">📖 Documentation</a></li>
      </ul>
    </div>
    <div class="navbar-end">
      <ThemeButton />
    </div>
  </div>
</template>
