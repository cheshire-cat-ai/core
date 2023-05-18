<script setup lang="ts">
</script>

<template>
	<div class="navbar sticky top-0 z-40 min-h-fit bg-base-100 font-medium shadow-xl md:px-[5%] lg:px-[10%]">
		<div class="navbar-start">
			<RouterLink to="/" class="shrink-0">
				<img src="@assets/logo.svg" class="hidden h-8 w-8 cursor-pointer md:block">
			</RouterLink>
			<Menu v-slot="{ open }" as="div" class="relative inline-block rounded md:hidden">
				<MenuButton class="btn-ghost btn-square btn" title="Menu">
					<heroicons-x-mark-20-solid v-if="open" class="swap-on h-6 w-6" />
					<heroicons-bars-3-solid v-else class="swap-off h-6 w-6" />
				</MenuButton>
				<Transition enter-active-class="transition duration-200 ease-out"
					enter-from-class="transform scale-90 opacity-0" enter-to-class="transform scale-100 opacity-100"
					leave-active-class="transition duration-200 ease-in" leave-from-class="transform scale-100 opacity-100"
					leave-to-class="transform scale-90 opacity-0">
					<MenuItems as="ul"
						class="menu menu-compact absolute left-0 z-50 mt-4 w-min origin-top-left gap-2 whitespace-nowrap rounded bg-base-100 p-2 shadow-xl">
						<MenuItem as="li">
							<RouterLink to="/">
								🏠️ Home
							</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<RouterLink to="/memory">
								🧠 Memory
							</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<RouterLink to="/plugins">
								🔌 Plugins
							</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<RouterLink to="/settings">
								⚙️ Settings
							</RouterLink>
						</MenuItem>
						<MenuItem as="li">
							<a href="https://pieroit.github.io/cheshire-cat" target="_blank">📖 Docs</a>
						</MenuItem>
					</MenuItems>
				</Transition>
			</Menu>
		</div>
		<div class="navbar-center">
			<RouterLink to="/" class="shrink-0">
				<img src="@assets/logo.svg" class="h-10 w-10 cursor-pointer md:hidden">
			</RouterLink>
			<ul class="menu menu-compact menu-horizontal hidden gap-2 px-1 md:flex">
				<li>
					<RouterLink to="/">
						🏠️ Home
					</RouterLink>
				</li>
				<li>
					<RouterLink to="/memory">
						🧠 Memory
					</RouterLink>
				</li>
				<li>
					<RouterLink to="/plugins">
						🔌 Plugins
					</RouterLink>
				</li>
				<li>
					<RouterLink to="/settings">
						⚙️ Settings
					</RouterLink>
				</li>
				<li><a href="https://pieroit.github.io/cheshire-cat" target="_blank">📖 Docs</a></li>
			</ul>
		</div>
		<div class="navbar-end">
			<ThemeButton />
		</div>
	</div>
</template>
