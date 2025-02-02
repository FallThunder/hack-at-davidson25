<script lang="ts">
    import type {BestMatch, Business} from "$lib/index";
    import {CheckIcon, MapPinIcon, PhoneIcon, MailIcon} from "lucide-svelte";
    import Chip from "./Chip.svelte";

    interface Props {
        match: BestMatch,
        business: Business
    }
    let { match, business }: Props = $props();
</script>

{#if business !== undefined}
    <div class="flex flex-row justify-center">
        <div class="flex flex-initial flex-col gap-3 bg-slate-800/50 backdrop-blur-sm w-96 p-6 rounded-xl shadow-xl hover:scale-105 hover:shadow-2xl transition-all duration-300 border-2 border-yellow-400/50">
            <div class="flex items-center gap-2">
                <div 
                    role="button"
                    tabindex="0"
                    on:click={() => {
                        if (business.homepage_link) {
                            window.open(business.homepage_link, '_blank', 'noopener,noreferrer');
                        }
                    }}
                    on:keydown={(e) => {
                        if (e.key === 'Enter' && business.homepage_link) {
                            window.open(business.homepage_link, '_blank', 'noopener,noreferrer');
                        }
                    }}
                    class="transition-colors"
                >
                    <h1 class="font-bold text-2xl {business.homepage_link ? 'text-white hover:text-yellow-400 cursor-pointer' : 'text-gray-300'}">{business.business_info.business_name}</h1>
                </div>
                <Chip 
                    text="Best Match" 
                    tooltip="This business best matches your search criteria"
                    color="yellow"
                />
            </div>
            <div class="space-y-2">
                <p class="font-medium text-sm text-yellow-400">
                    Pine thinks this is your best choice because:
                </p>
                <ul class="space-y-2">
                    {#each match.match_reasons as reason}
                        <li class="flex flex-row gap-2 items-start text-gray-300">
                            <CheckIcon class="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
                            <span>{reason}</span>
                        </li>
                    {/each}
                </ul>
            </div>
            <div class="space-y-2 mt-2">
                <div 
                    role="button"
                    tabindex="0"
                    on:click|stopPropagation={() => {
                        if (business.business_info.phone_number) {
                            window.location.href = `tel:${business.business_info.phone_number}`;
                        }
                    }}
                    on:keydown|stopPropagation={(e) => {
                        if (e.key === 'Enter' && business.business_info.phone_number) {
                            window.location.href = `tel:${business.business_info.phone_number}`;
                        }
                    }}
                    class="w-full flex flex-row gap-2 items-center text-gray-300 hover:text-yellow-400 transition-colors"
                >
                    <PhoneIcon class="w-5 h-5 text-yellow-400" />
                    <span>{business.business_info.phone_number}</span>
                </div>
                <div 
                    role="button"
                    tabindex="0"
                    on:click|stopPropagation={() => {
                        if (business.business_info.address) {
                            window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(business.business_info.address)}`, '_blank', 'noopener,noreferrer');
                        }
                    }}
                    on:keydown|stopPropagation={(e) => {
                        if (e.key === 'Enter' && business.business_info.address) {
                            window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(business.business_info.address)}`, '_blank', 'noopener,noreferrer');
                        }
                    }}
                    class="w-full flex flex-row gap-2 items-start text-gray-300 hover:text-yellow-400 transition-colors"
                >
                    <MapPinIcon class="w-5 h-5 text-yellow-400 flex-shrink-0 mt-1" />
                    <span>{business.business_info.address}</span>
                </div>
                {#if business.business_info.email}
                    <div 
                        role="button"
                        tabindex="0"
                        on:click|stopPropagation={() => {
                            window.location.href = `mailto:${business.business_info.email}`;
                        }}
                        on:keydown|stopPropagation={(e) => {
                            if (e.key === 'Enter') {
                                window.location.href = `mailto:${business.business_info.email}`;
                            }
                        }}
                        class="w-full flex flex-row gap-2 items-start text-gray-300 hover:text-yellow-400 transition-colors"
                    >
                        <MailIcon class="w-5 h-5 text-yellow-400 flex-shrink-0 mt-1" />
                        <span>{business.business_info.email}</span>
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}

