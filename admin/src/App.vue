<script setup lang="ts">

</script>

<template>
	<div class="flex min-h-screen flex-col scroll-smooth bg-base-100 text-sm transition-colors selection:bg-primary md:text-base">
		<Header />
		<NotificationStack />
		<RouterView v-slot="{ Component }" class="grow p-2 md:p-4">
			<template v-if="Component">
				<Transition mode="out-in"
					enter-active-class="animate__animated animate__fadeIn animate__fastest"
					leave-active-class="animate__animated animate__fadeOut animate__fastest">
					<KeepAlive>
						<component :is="Component" />
					</KeepAlive>
				</Transition>
			</template>
		</RouterView>
	</div>
</template>
