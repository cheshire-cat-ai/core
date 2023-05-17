<script setup lang="ts">

</script>

<template>
	<div class="flex flex-col items-center justify-evenly text-center">
		<p class="text-5xl font-bold">
			<span class="text-error">404</span>
			<br>
			<span class="text-neutral">Page Not Found</span>
		</p>
		<button class="btn-error btn rounded">
			<RouterLink to="/">
				Go back to Home!
			</RouterLink>
		</button>
	</div>
</template>
