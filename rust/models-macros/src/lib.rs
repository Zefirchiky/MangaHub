use proc_macro::TokenStream;
use quote::{format_ident, quote};
use syn::{parse_macro_input, DeriveInput};


#[proc_macro_attribute]
pub fn register_text_element(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as DeriveInput);
    let name = &input.ident;
    let parser_name = format_ident!("PARSER_{}", name.to_string().to_uppercase());
    let type_index = {
        const fn hash() -> usize {
            const_fnv1a_hash::fnv1a_hash_str_64(stringify!(#name)) as usize
        }
        hash()
    };
    
    let expanded = quote! {
        #input
        
        impl TextElementAuto for #name {
            // const TYPE_INDEX: usize = #type_index;

            fn type_index(&self) -> usize {
                #type_index
            }

            fn type_name(&self) -> &'static str {
                stringify!(#name)
            }
            
            fn as_any(&self) -> &dyn std::any::Any {
                self
            }
            
            fn as_any_mut(&mut self) -> &mut dyn std::any::Any {
                self
            }
        }

        #[linkme::distributed_slice(TEXT_ELEMENT_PARSERS)]
        static #parser_name: Parser = Parser {
            name: stringify!(#name),
            // handler: Box::<#name>new(),
            // type_index: #type_index,
            
            // from_token: |token| {
            //     let res = <#name>::try_from_token(token);
            //     if let crate::TokenParsingResult::Matched(el, tok) = res {
            //         TokenParsingResult::Matched(
            //             Box::new(el) as Box<dyn TextElementAuto>,
            //             tok
            //         )
            //     } else {
            //         res
            //     }
            // },
            from_token: |token| match <#name>::try_from_token(token) {
                crate::TokenParsingResult::Matched(el, tok) => TokenParsingResult::Matched(Box::new(el) as Box<dyn TextElementAuto>, tok),
                crate::TokenParsingResult::MatchedWithRest(tok1, tok2) => TokenParsingResult::MatchedWithRest(tok1, tok2),
                crate::TokenParsingResult::NotMatched(token) => crate::TokenParsingResult::NotMatched(token),
            },
            
            from_narration: |nar, cxt| Box::new(<#name>::from_narration(nar, cxt)) as Box<dyn TextElementAuto>,
        };
    };

    TokenStream::from(expanded)
}