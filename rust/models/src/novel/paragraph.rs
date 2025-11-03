use crate::{novel::{text_element::TextElementAuto, ElementEndState, Token}, registry::ParserRegistry};

type TextElPlugin = Box<dyn TextElementAuto>;

#[derive(Debug)]
pub struct Paragraph {
    elements: Vec<TextElPlugin>,
    last_end_state: ElementEndState,
    tokens_to_process: Vec<Token>,
}

impl Paragraph {
    pub fn new() -> Self {
        Self {
            elements: Vec::new(),
            last_end_state: ElementEndState::NotFinished,
            tokens_to_process: Vec::with_capacity(10),
        }
    }

    /// Extracts a token from the last end state if it is finished or maybe finished
    /// and queues it up for processing. Does nothing if the last end state is not finished.
    fn extract_and_queue_buffered_token(&mut self) {
        if let Some(tok) = match &mut self.last_end_state {
            ElementEndState::Finished(tok) | ElementEndState::MaybeFinished(tok) => tok.take(),
            _ => None,
        } {
            self.tokens_to_process.push(tok);
        }
    }

    /// Pushes a token to the paragraph and processes it according to the
    /// paragraph's last end state.
    ///
    /// If the last end state is `Finished` with a buffered token, the
    /// buffered token is processed next and the current token is pushed back
    /// to process later.
    ///
    /// If the last end state is `MaybeFinished` with a buffered token, the
    /// buffered token is processed next and the current token is pushed back
    /// to process later, and the last end state is reset to `MaybeFinished`
    /// without a buffered token.
    ///
    /// If the last end state is `NotFinished`, the current token is processed
    /// and the last end state is updated to the result of the processing.
    ///
    /// After processing the token, any buffered tokens are extracted from the
    /// last end state and queued for later processing.
    ///
    /// Returns a mutable reference to the paragraph.
    pub fn push_token(&mut self, token: Token) -> &mut Self {
        // dbg!(&token);
        self.tokens_to_process.push(token);
    
        while let Some(token) = self.tokens_to_process.pop() {
            if self.elements.is_empty() {
                let (mut new, token, tok) = ParserRegistry::parse_text_element_token(token);
                if let Some(tok) = tok {
                    self.tokens_to_process.push(tok);
                }
                new.push_token(token);
                self.elements.push(new);
                continue;
            }
            
            match &mut self.last_end_state {
                ElementEndState::Finished(buffered_token) => {
                    if let Some(tok) = buffered_token.take() {
                        // Push current token back to process later
                        self.tokens_to_process.push(token);
                        // Process buffered token next
                        self.tokens_to_process.push(tok);
                    } else {
                        let (mut new, token, tok) = ParserRegistry::parse_text_element_token(token);
                        if let Some(tok) = tok {
                            self.tokens_to_process.push(tok);
                        }
                        new.push_token(token);
                        self.elements.push(new);
                    }
                }
                ElementEndState::MaybeFinished(buffered_token) => {
                    if let Some(tok) = buffered_token.take() {
                        self.tokens_to_process.push(token);
                        self.tokens_to_process.push(tok);
                    } else {
                        let last = self.elements.last_mut().unwrap();
                        let (mut new, token, tok) = ParserRegistry::parse_text_element_token(token);
                        if let Some(tok) = tok {
                            self.tokens_to_process.push(tok);
                        }

                        // If last element was the same as new one, we can `merge` them
                        if last.type_index() == new.type_index() {
                            self.last_end_state = last.push_token(token);
                        } else {
                            self.last_end_state = new.push_token(token);
                            self.elements.push(new);
                        }
                        self.extract_and_queue_buffered_token();
                    }
                }
                ElementEndState::NotFinishedToken(..) => {
                    let old_state = std::mem::replace(&mut self.last_end_state, ElementEndState::NotFinished);
                    if let ElementEndState::NotFinishedToken(t1, t2) = old_state {
                        self.tokens_to_process.push(t1);
                        self.tokens_to_process.push(t2);
                    }
                }
                ElementEndState::NotFinished => {
                    self.last_end_state = self.elements.last_mut().unwrap().push_token(token);
                    self.extract_and_queue_buffered_token();
                }
            }
        }
        
        self
    }
}


#[cfg(test)]
mod novel_paragraph {
    use crate::novel::{text_element::Dialog, Paragraph, Token};

    #[test]
    // #[should_panic]
    fn parse_dialog_token() {
        let mut p = Paragraph::new();
        p.push_token(Token::new("This"));
        p.push_token(Token::new("nuh."));
        p.push_token(Token::new("That"));
        p.push_token(Token::new("that2\""));
        p.push_token(Token::new("dih"));
        p.push_token(Token::new("\"that3"));
        // dbg!(&p);
        assert!(p.elements[0].as_any().is::<Dialog>());
    }
}