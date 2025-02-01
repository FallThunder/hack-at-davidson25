<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<div class="min-h-screen min-w-screen bg-slate-800 text-pink-50 font-sans px-3 py-2">
    {@render children()}
</div>
