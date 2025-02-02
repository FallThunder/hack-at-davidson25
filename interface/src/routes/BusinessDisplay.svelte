<script lang="ts">
    interface Props {
        data: {
            match_count: number;
            matched_businesses: Array<{
                business_link: string;
                card_link: string;
            }>;
        } | undefined;
    }
    let { data }: Props = $props();
</script>

{#if data === undefined || data === null || data.match_count === 0}
    <i>Pine couldn't find anything that matches your needs.</i>
{:else}
    <div class="flex flex-row gap-4 flex-wrap flex-auto justify-center">
        {#each data.matched_businesses as business}
            <div class="flex flex-col gap-2 p-4 border border-pink-500 rounded-lg">
                <a href={business.business_link} target="_blank" rel="noopener noreferrer" class="text-pink-500 hover:text-pink-400">
                    <img src={business.card_link} alt="Business Card" class="max-w-[300px] rounded-lg shadow-lg hover:shadow-xl transition" />
                </a>
            </div>
        {/each}
    </div>
{/if}