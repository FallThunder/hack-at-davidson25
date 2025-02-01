export interface Business {
    name: string,
    phone: string,
    website: string,
    address: { street: string, city: string, state: string },
    description: string,
}

export interface BResponse {
    best_match: BestMatch,
    businesses: Business[]
}

export interface BestMatch {
    business_index: number,
    match_reasons: string[]
}