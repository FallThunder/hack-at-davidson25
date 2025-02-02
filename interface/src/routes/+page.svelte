<script lang="ts">
	import { CheckIcon, MailIcon, MapPinIcon, PhoneIcon } from 'lucide-svelte';
	import BusinessDisplay from "$lib/BusinessDisplay.svelte";
	import LoadingAnimation from "$lib/LoadingAnimations.svelte";
	import type {BResponse} from "$lib";

	let prompt = $state('');

	let promise: Promise<Response> | null = $state(null);
	let disabled = $state(false);
	let data: BResponse | undefined = $state(undefined);

	let error: string | null = $state(null);

	async function sub() {
		disabled = true;
		error = null;
		promise = fetch('https://ai-query-assistant-tacv2fcyxa-ue.a.run.app/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				query: prompt
			})
		});
		promise
				.then(async (d) => {
					const responseText = await d.text();
					console.log('Raw response:', responseText);
					data = parseData(responseText);
					console.log('Parsed data:', data);
					disabled = false;
				})
				.catch((e) => {
					console.error('Error:', e);
					error = e.toString();
					disabled = false;
				});
	}


	function parseData(d: string): any {
		try {
			// First try to parse the response as JSON directly
			try {
				return JSON.parse(d);
			} catch (e) {
				// If direct parsing fails, try to clean up the response
				let data = d;
				data = data.replaceAll('```json', '');
				data = data.replaceAll('```', '');
				if (data.startsWith('"')) {
					data = data.substring(1);
				}
				if (data.endsWith('"')) {
					data = data.substring(0, data.length - 1);
				}
				data = data.replaceAll('\\n', '');
				data = data.replaceAll('\\"', '"');
				data = data.replaceAll('\\\\"', '');

				console.log('Cleaned data:', data);
				return JSON.parse(data);
			}
		} catch (e: unknown) {
			console.error('Parse error:', e);
			error = e instanceof Error ? e.toString() : 'Unknown error occurred';
			return null;
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
	<div class="flex flex-col gap-6">
		<div class="flex flex-col items-center gap-4">
			<div class="text-center">
				<h1 class="text-4xl font-bold text-white mb-2 flex items-center gap-2 justify-center">
					<MapPinIcon class="w-8 h-8 text-pink-500" />
					Labor Locator
				</h1>
				<p class="text-lg text-pink-200 font-medium">Discover Lake Norman, One Business at a Time</p>
			</div>

			<p class="text-lg text-gray-300 text-center max-w-2xl">
				Looking for something specific in Lake Norman? Just ask Pine, our smart assistant, and we'll help you find the perfect local business!
			</p>

			<form
					class="flex-grow min-w-[60vw] flex flex-row gap-0 shadow-lg"
					onsubmit={(e) => {
					e.preventDefault();
					sub();
				}}
			>
				<input
						{disabled}
						bind:value={prompt}
						type="text"
						placeholder="Search for restaurants, plumbers, gyms..."
						class="flex-1 min-w-[50%] disabled:bg-slate-800 disabled:border-gray-600 disabled:cursor-not-allowed rounded-l-lg bg-slate-700 border-2 border-r-0 ring-0 focus:ring-0 focus:outline-none border-pink-500 py-3 px-4 text-gray-100 placeholder-gray-400"
				/>
				<button
						{disabled}
						class="bg-pink-500 disabled:bg-gray-600 disabled:hover:bg-gray-600 disabled:cursor-not-allowed hover:bg-pink-600 transition px-8 py-3 rounded-r-lg font-semibold text-white flex items-center gap-2"
				>
					Search
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
					</svg>
				</button>
			</form>
		</div>

		{#if promise !== null}
			{#await promise}
				<LoadingAnimation />
			{:then}
				{#if error === null}
					<BusinessDisplay {data} />
				{:else}
					<div class="flex flex-row justify-center">
						<span class="italic text-red-400 font-semibold">Something went wrong :( {error}</span>
					</div>
				{/if}
			{:catch e}
				<div class="flex flex-row justify-center">
					<span class="italic text-red-400 font-semibold">Something went wrong :( {e}</span>
				</div>
			{/await}
		{/if}
	</div>
</div>
