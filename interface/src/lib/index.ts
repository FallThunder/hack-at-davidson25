export interface Business {
    name: string,
    phone: string,
    website: string,
    address: string,
    match_reasons: string[]
}

export interface BResponse {
    best_match: BestMatch,
    businesses: Business[]
}

export interface BestMatch {
    business_index: number,
    match_reasons: string[]
}