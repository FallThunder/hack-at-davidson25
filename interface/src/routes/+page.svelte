<script lang="ts">
	import { CheckIcon, MailIcon, MapPinIcon, PhoneIcon } from 'lucide-svelte';
	import BusinessDisplay from "./BusinessDisplay.svelte";

	let prompt = $state('');

	let promise: Promise<Response> | null = $state(null);
	let disabled = $state(false);
	let data: {
		match_count: number;
		matched_businesses: Array<{
			business_link: string;
			card_link: string;
		}>;
	} | undefined = $state(undefined);

	async function sub() {
		disabled = true;
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

	let error: string | null = $state(null);
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

<div class="flex flex-col gap-2">
	<div class="flex flex-col items-center gap-2">
		<h1 class="text-3xl font-semibold text-center">LaborLocator</h1>

		<p class="text-lg text-center">Need help finding a business in the Lake Norman community? Our intelligent assistant Pine will help you find what you're looking for? Simply type in natural language what you're looking for below.</p>

		<form
			class="flex-grow min-w-[60vw] flex flex-row gap-3"
			onsubmit={(e) => {
				e.preventDefault();
				sub();
			}}
		>
			<input
				{disabled}
				bind:value={prompt}
				type="text"
				placeholder="What are you looking for?"
				class="flex-1 min-w-[50%] disabled:border-gray-600 disabled:cursor-not-allowed rounded bg-slate-700 border-2 ring-0 focus:ring-0 focus:outline-none border-pink-500 py-2 px-3"
			/>
			<button
				{disabled}
				class="bg-pink-500 disabled:bg-gray-600 disabled:hover:bg-gray-600 disabled:cursor-not-allowed hover:bg-pink-700 transition px-4 py-2 rounded font-semibold"
				>Go &rarr;</button
			>
		</form>
	</div>

	{#if promise !== null}
		{#await promise}
			<div class="flex flex-row justify-center">
				<span class="italic"
					>Pine is searching thousands of businesses for your best choice. This will only take a moment...
					seconds.</span
				>
			</div>
		{:then}
			{#if error === null}
				<BusinessDisplay {data} />
			{:else}
				<div class="flex flex-row justify-center">
					<span class="italic text-red-500 font-semibold">Something went wrong :( {error}</span>
				</div>
			{/if}
		{:catch e}
			<div class="flex flex-row justify-center">
				<span class="italic text-red-500 font-semibold">Something went wrong :( {e}</span>
			</div>
		{/await}
	{/if}
</div>
