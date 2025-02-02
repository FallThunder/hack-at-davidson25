// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

    interface SpeechRecognitionEvent {
        results: {
            [index: number]: {
                [index: number]: {
                    transcript: string;
                };
            };
        };
    }

    interface SpeechRecognition {
        continuous: boolean;
        interimResults: boolean;
        lang: string;
        start: () => void;
        stop: () => void;
        onresult: (event: SpeechRecognitionEvent) => void;
        onend: () => void;
        onerror: () => void;
    }

    interface Window {
        webkitSpeechRecognition: {
            new(): SpeechRecognition;
        };
    }
}

export {};
