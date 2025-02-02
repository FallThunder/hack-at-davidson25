export interface Business {
    business_info: BusinessInfo,
    card_link: string,
    homepage_link: string
}

export interface BusinessInfo {
    address: string,
    any_other_details: string,
    business_name: string,
    email: string,
    owner_name: string,
    phone_number: string
}

export interface BResponse {
    match_count: number,
    matched_businesses: Business[]
}
