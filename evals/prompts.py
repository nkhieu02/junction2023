ENTITY = '''Given a context and a completion, write diverse alternative completions that contradict the original completion meaning. First, identify if the completion contains an entity. Then, write the contradiction by modifying an entity or it’s property, add additional modifications if necessary. Make sure the changes you make are minimal (so only change necessary details to make the sentence plausible). Do not modify dates or quantities.
##
Context: "Sorry" is a song by American singer Madonna from her tenth studio album Confessions on a Dance Floor (2005). It was written and produced by Madonna and Stuart Price, and released as the second single from the album on February 7, 2006. It later appeared on Celebration, her 2009 greatest hits album. An uptempo dance song, " Sorry " was one of the first tracks developed for the album and had numerous remix treatments before the ultimate version of the track was finalized.
Completion: One of the remixes was done by the known band the Pet Shop Boys, featuring added lyrics by the band.
1. Change: "Pet Shop Boys" to "Maddona".
Contradiction: One of the remixes was done by the known singer Maddona, featuring added lyrics by the singer. 2. Change: "Pet Shop Boys" to "Depeche Mode".
Contradiction: One of the remixes was done by the known band Depeche Mode, featuring added lyrics by the band.
3. Change: "known" to "unfamiliar".
Contradiction: One of the remixes was done by the unfamiliar band Pet Shop Boys, featuring added lyrics by the band.
4. Change: "Pet Shop Boys" to "the Killers".
Contradiction: One of the remixes was done by the known band the Killers, featuring added lyrics by the band.
##
Context: {context}
Completion: {completion}'''

CIRCUMSTANCES = '''Given a context and a completion, write diverse alternative completions that contradict the original completion meaning. First, identify if the completion describes the circumstances of an event (location or time). If circumstances are mentioned, modify it to contradict the completion. Do not add time or location if they didn’t appear in the original completion. Make sure the changes you make are minimal.
##
Context: The kingdom had been in long gradual decline since the early 13th century. Had Pagan possessed a stronger central government, the collapse could have been temporary, and the country "could have risen again". But the dynasty could not recover, and because the Mongols refused to fill the power vacuum, no viable center emerged in the immediate aftermath. As a result, several minor states fought it out for supremacy for the better part of the 14th century. Completion: It was only in the late 14th century that two relatively strong powers emerged in the Irrawaddy basin, restoring some semblance of normalcy.
1. Change: "14th" to "15th".
Contradiction: It was only in the late 15th century that two relatively strong powers emerged in the Irrawaddy basin, restoring some semblance of normalcy. 2. Change: "Irrawaddy" to "Chindwin".
Contradiction: It was only in the late 14th century that two relatively strong powers emerged in the Chindwin basin, restoring some semblance of normalcy.
3. Change: "late" to "mid".
Contradiction: It was only in the mid 14th century that two relatively strong powers emerged in the Irrawaddy basin, restoring some semblance of normalcy.
##
Context: {context}
Completion: {completion}'''

COREFERENCE = '''Given a context and a completion, write diverse alternative completions that contradict the original completion meaning. First, decide if the completion contains a pronoun (such as: he, she, it, they, his, her, its, theirs...) and write the entity it refers to. Write the contradiction by modifying the pronoun to contradict the original coreference.
##
Context: His stance in favor of prohibition cost him the votes of four legislators in his own party and the seat went to Republican William O. Bradley. Six years later Beckham secured the seat by popular election, but he lost his re-election bid largely because of his pro-temperance views and his opposition to women’s suffrage.
Completion: Though he continued to play an active role in state politics for another two decades, he never returned to elected office, failing in his gubernatorial bid in 1927 and his senatorial campaign in 1936.
1. Pronoun: he
Change: "he" to "Bradley".
Contradiction: Though Bradley continued to play an active role in state politics for another two decades, he never returned to elected office, failing in his gubernatorial bid in 1927 and his senatorial campaign in 1936.
2. Pronoun: he
Change: "he" to "Bradley".
Contradiction: Though he continued to play an active role in state politics for another two decades, Bradley never returned to elected office, failing in his gubernatorial bid in 1927 and his senatorial campaign in 1936.
3. Pronoun: his
Change: "his" to "Bradley’s".
Contradiction: Though he continued to play an active role in state politics for another two decades, he never returned to elected office, failing in Bradley’s gubernatorial bid in 1927 and his senatorial campaign in 1936.
##
Context: The early 6th century saw another queen ruling the city, known only as the "Lady of Tikal", who was very likely a daughter of Chak Tok Ich ’aak II.
Completion: She seems never to have ruled in her own right, rather being partnered with other rulers.
1. Pronoun: She
Change: "She" to "He" and "her" to "his".
Contradiction: He seems never to have ruled in his own right, rather being partnered with other rulers.
2. Pronoun: She
Change: "She" to "The king" and "her" to "his".
Contradiction: The king seems never to have ruled in his own right, rather being partnered with other rulers.
3. Pronoun: She
Change: "She" to "Chak Tok Ich".
Contradiction: Chak Tok Ich seems never to have ruled in her own right, rather being partnered with other rulers.
##
Context: {context}
Completion: {completion}'''

PREDICATE = '''Given a context and a completion, write diverse alternative completions, that contradict the original completion meaning by modifying verbs. First, Identify a verb in the original completion, and then write the contradiction by modifying it. Make sure the contradictions are grammatically correct, fluent and consistent. Make any necessary additional modifications to ensure that.
##
Context: Homarus gammarus is a large crustacean, with a body length up to 60 centimetres (24 in) and weighing up to 5 – 6 kilograms (11 – 13 lb), although the lobsters caught in lobster pots are usually 23 – 38 cm (9 – 15 in) long and weigh 0.7 – 2.2 kg (1.5 – 4.9 lb).
Completion: Like other crustaceans, lobsters have a hard exoskeleton which they must shed in order to grow, in a process called ecdysis (moulting).
1. Change: "shed" to "retain". Additional changes: "in order to grow" to "in order to survive".
Contradiction: Like other crustaceans, lobsters have a hard exoskeleton which they must retain in order to survive, in a process called ecdysis (moulting).
2. Change: "grow" to "maintain their size".
Contradiction: Like other crustaceans, lobsters have a hard exoskeleton which they must shed in order to maintain their size, in a process called ecdysis (moulting).
3. Change: "shed" to "keep". Additional changes: "in order to grow" to "in order to strengthen".
Contradiction: Like other crustaceans, lobsters have a hard exoskeleton which they must keep in order to strengthen, in a process called ecdysis (moulting).
##
Context: The ridge offered a natural avenue of approach to the airfield, commanded the surrounding area and was almost undefended. Edson and Thomas tried to persuade Vandegrift to move forces to defend the ridge, but Vandegrift refused, believing that the Japanese were more likely to attack along the coast.
Completion: Finally, Thomas convinced Vandegrift that the ridge was a good location for Edson’s Raiders to rest from their actions of the preceding month.
1. Change: "rest" to "keep up".
Contradiction: Finally, Thomas convinced Vandegrift that the ridge was a good location for Edson’s Raiders to keep up with their actions of the preceding month.
2. Change: "convinced Vandegrift" to "made Vandegrift doubt".
Contradiction: Finally, Thomas made Vandegrift doubt that the ridge was a good location for Edson’s Raiders to rest from their actions of the preceding month. 3. Change: "rest" to "continue".
Contradiction: Finally, Thomas convinced Vandegrift that the ridge was a good location for Edson’s Raiders to continue their actions of the preceding month.
##
Context: {context}
Completion: {completion}'''


LINK = '''Given a sentence, write contradictory sentences by modifying a temporal link. First, identify a link between events, and then modify it. Make sure the contradictions are grammatically correct and fluent. If no such link exists, answer "NA".
##
Sentence: Prior to filming, a week was spent reinforcing the roof of the liquor store to ensure it would not collapse if it were to be intruded by a group of fans.
1. Change: "prior to" to "after".
Contradiction: After filming, a week was spent reinforcing the roof of the liquor store to ensure it would not collapse if it were to be intruded by a group of fans.
##
Sentence: Lewis McAllister, a businessman in Tuscaloosa, Alabama, was the first Republican to serve in the Mississippi House of Representatives since Reconstruction, 1962-1968; he resided in Meridian prior to 1971.
1. Change: "prior to" to "after".
Contradiction: Lewis McAllister, a businessman in Tuscaloosa, Alabama, was the first Republican to serve in the Mississippi House of Representatives since Reconstruction, 1962-1968; he resided in Meridian after 1971.
2. Change: "since" to "before"
Contradiction: Lewis McAllister, a businessman in Tuscaloosa, Alabama, was the first Republican to serve in the Mississippi House of Representatives before Reconstruction, 1962-1968; he resided in Meridian prior to 1971.
##
Sentence: The decline of the railroad industry caused significant job losses, resulting in a population decline as workers left for other areas.
1. Change: "caused" to "caused by".
Contradiction: The decline of the railroad industry, caused by significant job losses, resulting a population decline as workers left for other areas.
2. Change: "resulting" to "was the result of".
Contradiction: The decline of the railroad industry caused significant job losses, was the result of a population decline, as workers left for other areas.
##
Sentence: {completion}'''



ERRORS = {'ENTITY': ENTITY, 'PREDICATE': PREDICATE, 
          'COREFERENCE': COREFERENCE,'CIRCUMSTANCES': CIRCUMSTANCES, 
          'LINK': LINK}




