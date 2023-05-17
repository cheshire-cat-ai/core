<script setup lang="ts">
import { useNotifications } from '@stores/useNotifications'

const { getNotifications } = useNotifications()
</script>

<template>
	<div class="toast-end toast toast-top !top-16 z-50 md:!top-12">
		<TransitionGroup name="notifications">
			<div v-for="notification in getNotifications()" 
				:key="notification.id" class="alert py-2 font-medium text-base-100" :class="{
					'hidden': notification.hidden,
					'alert-info': notification.type === 'info',
					'alert-error': notification.type === 'error',
					'alert-success': notification.type === 'success'
				}">
				<div>
					<span>{{ notification.text }}</span>
				</div>
			</div>
		</TransitionGroup>
	</div>
</template>

<style scoped>
.notifications-move, .notifications-enter-active, .notifications-leave-active {
    transition: all 0.5s ease;
}

.notifications-enter-from, .notifications-leave-to {
    opacity: 0;
    transform: translateX(30px);
}
</style>