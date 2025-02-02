<script lang="ts">
    import type {Business} from "$lib/index";
    import {MailIcon, MapPinIcon, PhoneIcon, UserRoundIcon} from "lucide-svelte";

    interface Props {
        business: Business
    }
    let { business }: Props = $props();
</script>

<div class="flex flex-row justify-center">
    <div class="flex flex-initial flex-col gap-3 bg-slate-800/50 backdrop-blur-sm w-96 p-6 rounded-xl shadow-xl hover:scale-105 hover:shadow-2xl transition-all duration-300 border border-slate-700">
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
            <h1 class="font-bold text-xl {business.homepage_link ? 'text-white hover:text-pink-400 cursor-pointer' : 'text-gray-300'}">{business.business_info.business_name}</h1>
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
                class="w-full flex flex-row gap-2 items-center text-gray-300 hover:text-pink-400 transition-colors"
            >
                <PhoneIcon class="w-5 h-5 text-pink-400" />
                <span>{business.business_info.phone_number || 'Unavailable'}</span>
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
                class="w-full flex flex-row gap-2 items-start text-gray-300 hover:text-pink-400 transition-colors"
            >
                <MapPinIcon class="w-5 h-5 text-pink-400 flex-shrink-0 mt-1" />
                <span>{business.business_info.address || 'Unavailable'}</span>
            </div>
            <div 
                role="button"
                tabindex="0"
                on:click|stopPropagation={() => {
                    if (business.business_info.owner_name) {
                        window.open(business.card_link, '_blank', 'noopener,noreferrer');
                    }
                }}
                on:keydown|stopPropagation={(e) => {
                    if (e.key === 'Enter' && business.business_info.owner_name) {
                        window.open(business.card_link, '_blank', 'noopener,noreferrer');
                    }
                }}
                class="w-full flex flex-row gap-2 items-start text-gray-300 hover:text-pink-400 transition-colors"
            >
                <UserRoundIcon class="w-5 h-5 text-pink-400 flex-shrink-0 mt-1" />
                <span>{business.business_info.owner_name || 'Unavailable'}</span>
            </div>
            <div 
                role="button"
                tabindex="0"
                on:click|stopPropagation={() => {
                    if (business.business_info.email) {
                        window.location.href = `mailto:${business.business_info.email}`;
                    }
                }}
                on:keydown|stopPropagation={(e) => {
                    if (e.key === 'Enter' && business.business_info.email) {
                        window.location.href = `mailto:${business.business_info.email}`;
                    }
                }}
                class="w-full flex flex-row gap-2 items-start text-gray-300 hover:text-pink-400 transition-colors"
            >
                <MailIcon class="w-5 h-5 text-pink-400 flex-shrink-0 mt-1" />
                <span>{business.business_info.email || 'Unavailable'}</span>
            </div>
        </div>
    </div>

