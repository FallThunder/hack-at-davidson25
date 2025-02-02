<script lang="ts">
    import type {BestMatch, Business} from "$lib/index";
    import {CheckIcon, MapPinIcon, PhoneIcon} from "lucide-svelte";

    interface Props {
        business: Business
    }
    let { business }: Props = $props();
</script>

<div class="flex flex-row justify-center">
    <div
            class="flex flex-initial flex-col gap-3 bg-slate-800/50 backdrop-blur-sm min-w-80 p-5 rounded-xl shadow-xl hover:scale-105 hover:shadow-2xl cursor-pointer transition-all duration-300 border border-slate-700"
    >
        <h1 class="font-bold text-xl text-white">{business.name}</h1>
        <div class="space-y-2">
            <p class="font-medium text-sm text-pink-400">
                Pine thinks this is a good choice because:
            </p>
            <ul class="space-y-2">
                {#each business.match_reasons as reason}
                    <li class="flex flex-row gap-2 items-start text-gray-300">
                        <CheckIcon class="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                        <span>{reason}</span>
                    </li>
                {/each}
            </ul>
        </div>
        <div class="space-y-2 mt-2">
            <p class="flex flex-row gap-2 items-center text-gray-300">
                <PhoneIcon class="w-5 h-5 text-pink-400" />
                <span>{business.phone}</span>
            </p>
            <p class="flex flex-row gap-2 items-start text-gray-300">
                <MapPinIcon class="w-5 h-5 text-pink-400 flex-shrink-0 mt-1" />
                <span>{business.address}</span>
            </p>
        </div>
    </div>
</div>
