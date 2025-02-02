<script lang="ts">
    import type {BResponse, BestMatch, Business} from "$lib/index";
    import FeaturedBusinessCard from "./FeaturedBusinessCard.svelte";
    import BusinessCard from "./BusinessCard.svelte";

    interface Props {
        data: BResponse
    }
    let { data }: Props = $props();

    let bestMatch: BestMatch | null = $state(null);

    // Create best match object from API response
    $effect(() => {
        if (data?.best_match) {
            bestMatch = {
                match_reasons: [data.best_match.reason]
            };
        }
    });

    // Function to calculate information completeness score
    function getInfoScore(business: Business): number {
        let score = 0;
        const info = business.business_info;
        
        if (info.phone_number) score++;
        if (info.address) score++;
        if (info.email) score++;
        if (info.owner_name) score++;
        if (business.homepage_link) score++;
        if (info.any_other_details) score++;
        
        return score;
    }

    // Sort businesses by info completeness
    $effect(() => {
        if (data?.matched_businesses && data.matched_businesses.length > 1) {
            // Get all businesses except the first one (best match)
            const remainingBusinesses = data.matched_businesses.slice(1);
            
            // Sort by info score in descending order
            remainingBusinesses.sort((a, b) => getInfoScore(b) - getInfoScore(a));
            
            // Update the data with sorted businesses
            data.matched_businesses = [data.matched_businesses[0], ...remainingBusinesses];
        }
    });
</script>

{#if data === undefined || data.match_count === 0}
    <h2 class="text-center italic">Pine couldn't find any local businesses to meet your needs.</h2>
{:else}
    <div class="flex flex-col gap-8">
        {#if bestMatch && data.matched_businesses[0]}
            <FeaturedBusinessCard business={data.matched_businesses[0]} match={bestMatch} />
        {/if}
        <div class="flex flex-row gap-4 flex-wrap flex-auto justify-center">
            {#each data.matched_businesses.slice(1) as entry}
                <BusinessCard business={entry} />
            {/each}
        </div>
    </div>
{/if}
