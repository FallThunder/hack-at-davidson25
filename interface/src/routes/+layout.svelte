<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<div class="min-h-screen m-0 p-0 min-w-screen bg-slate-800 text-pink-50 font-sans">
	{@render children()}
</div>
