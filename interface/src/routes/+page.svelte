<script>
    import {MailIcon, MapPinIcon, PhoneIcon} from "lucide-svelte";

    let hasResults = false;
</script>

<div class="flex flex-col gap-2">
    <div class="flex flex-col items-center gap-2">
        <h1 class="text-3xl font-semibold text-center">LaborLocator</h1>

        <p class="text-lg text-center">Need help finding a business in the Lake Norman community?</p>

        <input type="text" placeholder="What are you looking for?" class="min-w-[50%] rounded bg-slate-700 border-2 ring-0 focus:ring-0 focus:outline-none border-thepink py-2 px-3" />
    </div>

    {#if hasResults}
        <div class="flex flex-row justify-center">
            <div class="flex flex-initial flex-col gap-2 bg-slate-900 min-w-80 px-3 py-2 rounded shadow-xl border border-yellow-400 hover:scale-105 cursor-pointer transition">
                <h1 class="font-semibold text-2xl">Business 1234</h1>
                <div>
                    <p class="font-light text-xs">Pine thinks this is <b class="font-bold text-yellow-400">your best choice because:</b></p>
                    <p>Blah blah</p>
                </div>
                <p class="flex flex-row gap-2 align-middle">
                    <PhoneIcon class="w-5 h-5" />
                    (111) 1111-11111
                </p>
                <p class="flex flex-row gap-2 align-middle">
                    <MapPinIcon class="w-5 h-5" />
                    123 Road St
                </p>
            </div>
        </div>

        <div class="flex flex-row items-center">
            <div class="flex flex-row flex-wrap gap-4 items-center mt-5">
                {#each {length: 50} as _, i}
                    <div class="flex-auto">
                        <div class="flex flex-col gap-2 bg-slate-900 min-w-80 px-3 py-2 rounded shadow-xl hover:scale-105 cursor-pointer transition">
                            <h1 class="font-semibold text-xl">Business {i}</h1>
                            <div>
                                <p class="font-light text-xs">Pine thinks this is relevant because:</p>
                                <p>Blah blah</p>
                            </div>
                            <p class="flex flex-row gap-2 align-middle">
                                <PhoneIcon class="w-5 h-5" />
                                ({i}{i}{i}) {i}{i}{i}-{i}{i}{i}{i}
                            </p>
                            <p class="flex flex-row gap-2 align-middle">
                                <MapPinIcon class="w-5 h-5" />
                                123 Road St
                            </p>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    {:else}
        <div class="flex flex-row justify-center">
            <span class="italic">Talk to Pine to get some business suggestions!</span>
        </div>
    {/if}
</div>