<script lang="ts">
    import { MapPinIcon, SearchIcon } from 'lucide-svelte';
</script>

<div class="flex flex-col items-center gap-4 py-8">
    <div class="relative">
        <!-- Animated cards stack -->
        <div class="relative w-48 h-32">
            {#each Array(3) as _, i}
                <div 
                    class="absolute w-full h-full bg-slate-700/50 backdrop-blur-sm border border-pink-500/20 rounded-lg shadow-lg"
                    style="
                        transform: translate({-5 + i * 5}px, {-5 + i * 5}px) rotate({-2 + i * 2}deg);
                        animation: float {2 + i * 0.2}s ease-in-out infinite alternate;
                    "
                >
                </div>
            {/each}
            
            <!-- Animated search icon -->
            <div 
                class="absolute -right-4 -top-4 w-8 h-8 bg-pink-500 rounded-full flex items-center justify-center"
                style="animation: searchMove 2s ease-in-out infinite"
            >
                <SearchIcon class="w-5 h-5 text-white" />
            </div>
        </div>
    </div>
    
    <div class="text-center">
        <p class="text-gray-300 font-medium">Pine is searching through local businesses</p>
        <div class="flex items-center justify-center gap-1 text-pink-400">
            <span class="animate-bounce" style="animation-delay: 0s">.</span>
            <span class="animate-bounce" style="animation-delay: 0.2s">.</span>
            <span class="animate-bounce" style="animation-delay: 0.4s">.</span>
        </div>
    </div>
</div>

<style>
    @keyframes float {
        from {
            transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) translateY(0px);
        }
        to {
            transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) translateY(-10px);
        }
    }

    @keyframes searchMove {
        0% {
            transform: translate(0, 0) rotate(0deg);
        }
        25% {
            transform: translate(-20px, 10px) rotate(-15deg);
        }
        75% {
            transform: translate(20px, 10px) rotate(15deg);
        }
        100% {
            transform: translate(0, 0) rotate(0deg);
        }
    }
</style>
