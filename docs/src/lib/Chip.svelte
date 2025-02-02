<script lang="ts">
    type ChipColor = 'yellow' | 'pink' | 'green';
    
    interface Props {
        text: string;
        tooltip?: string;
        color?: ChipColor;
    }

    let { text, tooltip = '', color = 'yellow' as ChipColor } = $props();

    const colorClasses: Record<ChipColor, string> = {
        yellow: 'bg-yellow-400/20 text-yellow-400',
        pink: 'bg-pink-400/20 text-pink-400',
        green: 'bg-green-400/20 text-green-400'
    };
</script>

<span 
    class="{colorClasses[color]} text-xs px-2 py-1 rounded-full font-medium relative group cursor-help"
    title={tooltip}
>
    {text}
    {#if tooltip}
        <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none z-50 shadow-lg">
            {tooltip}
            <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                <div class="border-4 border-transparent border-t-gray-900"></div>
            </div>
        </div>
    {/if}
</span>

<style>
    /* Add a small delay to prevent the tooltip from disappearing immediately when moving mouse */
    .group:hover .group-hover\:opacity-100 {
        transition-delay: 100ms;
    }
</style>
