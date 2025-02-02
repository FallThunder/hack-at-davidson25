<script lang="ts">
    import type {BResponse} from "$lib/index";
    import FeaturedBusinessCard from "./FeaturedBusinessCard.svelte";
    import BusinessCard from "./BusinessCard.svelte";

    interface Props {
        data: BResponse
    }
    let { data }: Props = $props();
</script>

{#if data === undefined || data === null}
    <i>Pine couldn't find anything that matches your needs.</i>
{:else}
    {#if data.best_match !== null && data.best_match !== undefined && data.best_match.business_index !== null && data.best_match.business_index !== undefined}
        <FeaturedBusinessCard match={data.best_match} business={data.businesses[data.best_match.business_index]} />
        {#if data.businesses && data.businesses.length !== 1}
            <h2 class="text-center italic">Other options may include:</h2>
        {:else}
            <h2 class="text-center italic">There are no other results!</h2>
        {/if}
    {/if}

    {#if data.businesses !== null && data.businesses !== undefined}
        <div class="flex flex-row gap-4 flex-wrap flex-auto justify-center">
            {#each data.businesses as entry, i}
                {#if (data.best_match.business_index !== null && data.best_match.business_index !== undefined && i === data.best_match.business_index)}
                    <!-- skip, we already showed this -->
                {:else}
                    <BusinessCard business={entry} />
                {/if}
            {:else}
                <h2 class="text-center italic">Pine couldn't find any local businesses to meet your needs.</h2>
            {/each}
        </div>
    {/if}
{/if}