<script lang="ts">
    import type {BestMatch, Business} from "$lib";
    import {CheckIcon, MapPinIcon, PhoneIcon} from "lucide-svelte";

    interface Props {
        match: BestMatch,
        business: Business
    }
    let { match, business }: Props = $props();
</script>

{#if business !== undefined}
<div class="flex flex-row justify-center">
    <div
            class="flex flex-initial flex-col gap-2 bg-slate-900 min-w-80 px-3 py-2 rounded shadow-xl border border-yellow-400 hover:scale-105 cursor-pointer transition"
    >
        <h1 class="font-semibold text-2xl">{business.name}</h1>
        <div>
            <p class="font-light text-xs">
                Pine thinks this is <b class="font-bold text-yellow-400"
            >your best choice because:</b
            >
            </p>
            <ul>
                {#each match.match_reasons as reason}
                    <li class="flex flex-row gap-2">
                        <CheckIcon class="text-green-500" />
                        {reason}
                    </li>
                {/each}
            </ul>
        </div>
        <p class="flex flex-row gap-2 align-middle">
            <PhoneIcon class="w-5 h-5" />
            {business.phone}
        </p>
        <p class="flex flex-row gap-2 align-middle">
            <MapPinIcon class="w-5 h-5" />
            {business.address.street}, {business.address.city}, {business.address.state}
        </p>
    </div>
</div>
    {/if}