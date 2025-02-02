<script lang="ts">
    import type {BResponse} from "$lib/index";
    import FeaturedBusinessCard from "./FeaturedBusinessCard.svelte";
    import BusinessCard from "./BusinessCard.svelte";

    interface Props {
        data: BResponse
    }
    let { data }: Props = $props();
</script>

{#if data === undefined || data.match_count === 0}
    <h2 class="text-center italic">Pine couldn't find any local businesses to meet your needs.</h2>
{:else}
    <div class="flex flex-row gap-4 flex-wrap flex-auto justify-center">
        {#each data.matched_businesses as entry}
            <BusinessCard business={entry} />
        {/each}
    </div>
{/if}