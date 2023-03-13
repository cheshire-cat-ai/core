import langchain
from langchain.llms import OpenAIChat
from langchain.embeddings import OpenAIEmbeddings

import time 
import os
from utils import log

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import langchain
from langchain.vectorstores import Qdrant


def get_vector_store(collection_name, embedder):

    qd_client = QdrantClient(host="vector-memory", port=6333) # TODO: should be configurable

    # create collection if it does not exist
    try:
        qd_client.get_collection(collection_name)
        tabula_rasa = False
        log(f'Collection "{collection_name}" already present in vector store')
    except:
        log(f'Creating collection {collection_name} ...')
        qd_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE), # TODO: if we change the embedder, how do we know the dimensionality?
        )
        tabula_rasa = True
        

    vector_memory = Qdrant(
        qd_client,
        collection_name,
        embedding_function=embedder.embed_query
    )

    if tabula_rasa:
        vector_memory.add_texts(
            ['I am the Cheshire Cat'],
            [{
                'who' : 'cheshire-cat',
                'when': time.time(),
                'text': 'I am the Cheshire Cat', 
            }]
        )
        
    log( dict(qd_client.get_collection(collection_name)) )

    return vector_memory




### Embedding LLM
# TODO: should be configurable via REST API
embedder = OpenAIEmbeddings(
    document_model_name='text-embedding-ada-002',
    openai_api_key=os.environ['OPENAI_KEY']
)

### Memory
episodic_memory    = get_vector_store('utterances', embedder=embedder)
declarative_memory = get_vector_store('documents', embedder=embedder)
# TODO: don't know if it is better to use different collections or just different metadata


user_message  ="""
Nel mezzo del cammin di nostra vita
mi ritrovai per una selva oscura
ché la diritta via era smarrita.
    Ahi quanto a dir qual era è cosa dura
esta selva selvaggia e aspra e forte
che nel pensier rinova la paura!
    Tant'è amara che poco è più morte;
ma per trattar del ben ch'i' vi trovai,
dirò de l'altre cose ch'i' v'ho scorte.
    Io non so ben ridir com'i' v'intrai,
tant'era pien di sonno a quel punto
che la verace via abbandonai.
    Ma poi ch'i' fui al piè d'un colle giunto,
là dove terminava quella valle
che m'avea di paura il cor compunto,
    guardai in alto, e vidi le sue spalle
vestite già de' raggi del pianeta
che mena dritto altrui per ogne calle.
    Allor fu la paura un poco queta
che nel lago del cor m'era durata
la notte ch'i' passai con tanta pieta.
    E come quei che con lena affannata
uscito fuor del pelago a la riva
si volge a l'acqua perigliosa e guata,
    così l'animo mio, ch'ancor fuggiva,
si volse a retro a rimirar lo passo
che non lasciò già mai persona viva.
    Poi ch'èi posato un poco il corpo lasso,
ripresi via per la piaggia diserta,
sì che 'l piè fermo sempre era 'l più basso.
    Ed ecco, quasi al cominciar de l'erta,
una lonza leggera e presta molto,
che di pel macolato era coverta;
    e non mi si partia dinanzi al volto,
anzi 'mpediva tanto il mio cammino,
ch'i' fui per ritornar più volte vòlto.
    Temp'era dal principio del mattino,
e 'l sol montava 'n sù con quelle stelle
ch'eran con lui quando l'amor divino
    mosse di prima quelle cose belle;
sì ch'a bene sperar m'era cagione
di quella fiera a la gaetta pelle
    l'ora del tempo e la dolce stagione;
ma non sì che paura non mi desse
la vista che m'apparve d'un leone.
    Questi parea che contra me venisse
con la test'alta e con rabbiosa fame,
sì che parea che l'aere ne tremesse.
    Ed una lupa, che di tutte brame
sembiava carca ne la sua magrezza,
e molte genti fé già viver grame,
    questa mi porse tanto di gravezza
con la paura ch'uscia di sua vista,
ch'io perdei la speranza de l'altezza.
    E qual è quei che volontieri acquista,
e giugne 'l tempo che perder lo face,
che 'n tutt'i suoi pensier piange e s'attrista;
    tal mi fece la bestia sanza pace,
che, venendomi 'ncontro, a poco a poco
mi ripigneva là dove 'l sol tace.
    Mentre ch'i' rovinava in basso loco,
dinanzi a li occhi mi si fu offerto
chi per lungo silenzio parea fioco.
    Quando vidi costui nel gran diserto,
«Miserere di me», gridai a lui,
«qual che tu sii, od ombra od omo certo!».
    Rispuosemi: «Non omo, omo già fui,
e li parenti miei furon lombardi,
mantoani per patria ambedui.
    Nacqui sub Iulio, ancor che fosse tardi,
e vissi a Roma sotto 'l buono Augusto
nel tempo de li dèi falsi e bugiardi.
    Poeta fui, e cantai di quel giusto
figliuol d'Anchise che venne di Troia,
poi che 'l superbo Ilión fu combusto.
    Ma tu perché ritorni a tanta noia?
perché non sali il dilettoso monte
ch'è principio e cagion di tutta gioia?».
    «Or se' tu quel Virgilio e quella fonte
che spandi di parlar sì largo fiume?»,
rispuos'io lui con vergognosa fronte.
    «O de li altri poeti onore e lume
vagliami 'l lungo studio e 'l grande amore
che m'ha fatto cercar lo tuo volume.
    Tu se' lo mio maestro e 'l mio autore;
tu se' solo colui da cu' io tolsi
lo bello stilo che m'ha fatto onore.
    Vedi la bestia per cu' io mi volsi:
aiutami da lei, famoso saggio,
ch'ella mi fa tremar le vene e i polsi».
    «A te convien tenere altro viaggio»,
rispuose poi che lagrimar mi vide,
«se vuo' campar d'esto loco selvaggio:
    ché questa bestia, per la qual tu gride,
non lascia altrui passar per la sua via,
ma tanto lo 'mpedisce che l'uccide;
    e ha natura sì malvagia e ria,
che mai non empie la bramosa voglia,
e dopo 'l pasto ha più fame che pria.
    Molti son li animali a cui s'ammoglia,
e più saranno ancora, infin che 'l veltro
verrà, che la farà morir con doglia.
    Questi non ciberà terra né peltro,
ma sapienza, amore e virtute,
e sua nazion sarà tra feltro e feltro.
    Di quella umile Italia fia salute
per cui morì la vergine Cammilla,
Eurialo e Turno e Niso di ferute.
    Questi la caccerà per ogne villa,
fin che l'avrà rimessa ne lo 'nferno,
là onde 'nvidia prima dipartilla.
    Ond'io per lo tuo me' penso e discerno
che tu mi segui, e io sarò tua guida,
e trarrotti di qui per loco etterno,
    ove udirai le disperate strida,
vedrai li antichi spiriti dolenti,
ch'a la seconda morte ciascun grida;
    e vederai color che son contenti
nel foco, perché speran di venire
quando che sia a le beate genti.
    A le quai poi se tu vorrai salire,
anima fia a ciò più di me degna:
con lei ti lascerò nel mio partire;
    ché quello imperador che là sù regna,
perch'i' fu' ribellante a la sua legge,
non vuol che 'n sua città per me si vegna.
    In tutte parti impera e quivi regge;
quivi è la sua città e l'alto seggio:
oh felice colui cu' ivi elegge!».
    E io a lui: «Poeta, io ti richeggio
per quello Dio che tu non conoscesti,
acciò ch'io fugga questo male e peggio,
    che tu mi meni là dov'or dicesti,
sì ch'io veggia la porta di san Pietro
e color cui tu fai cotanto mesti».
    Allor si mosse, e io li tenni dietro.
"""

history = ''
memories_separator = '\n  -'

episodic_memory_vectors = episodic_memory.max_marginal_relevance_search(user_message) # TODO: customize k and fetch_k
episodic_memory_text = [m.page_content for m in episodic_memory_vectors]
episodic_memory_content = memories_separator + memories_separator.join(episodic_memory_text) # TODO: take away duplicates; insert time information (e.g "two days ago")

declarative_memory_content = '' # TODO: search in uploaded documents!


# update conversation history
history += f'Human: {user_message}\n'
# history += f'AI: {cat_message["output"]}\n'        


# store user message in episodic memory
# TODO: also embed HyDE style
# TODO: vectorize and store conversation chunks
for m in user_message.split('\n'):
    if m != '':
        vector_ids = episodic_memory.add_texts(
            [m],
            [{
                #'who' : 'user', # TODO: is this necessary if there is a dedicated collection?
                # 'when': time.time(),
                'text': m, 
            }]
        )

        log(m)
        
        
# TODO: should we receive files also via websocket?
@cheshire_cat_api.post("/rabbithole/") 
async def rabbithole_upload(request: Request):
    form = await request.form()
    file: UploadFile = None    
    log("-------------------------------------------")
    log("parametri dell'upload'")
    log("-------------------------------------------")
    for f in form:
        log(f"{f} = {form[f]} -> {type(form[f])}, {type(form[f]).__name__ }")
        if type(form[f]).__name__ == "UploadFile":
            file = form[f]
    log("-------------------------------------------")
    
    log(str(request.client))
    log(str(request.url))
    log(str(request.headers))
    log(str(request.query_params))
    log(str(request.cookies))
    log(str(request.path_params))
    log(str(request.url.path))

    # list of admitted MIME types
    admitted_mime_types = [
        'text/plain'
    ]
    
    # check id MIME type of uploaded file is supported
    if file.content_type not in admitted_mime_types:
        return {
            'error': f'MIME type {file.content_type} not supported. Admitted types: {" - ".join(admitted_mime_types)}'
        }

    # read file content
    # TODO: manage exceptions
    content = await file.read()
    content = str(content, 'utf-8')


    # TODO: use langchain splitters
    # TODO: also use an overlap window between docs and summarizations
    docs = content.split('\r\n')
    
    # remove duplicates
    docs = list(set(docs))
    log(len(docs))
    docs = [doc.strip() for doc in docs]
    log(len(docs))
    try:
        docs.remove('')
    except ValueError as e:
        log(f"Error: {e}")
    log(f'Preparing to memorize {len(docs)} vectors')

    # TODO: add metadata to the content itself citing the source??

    # classic embed
    for doc in docs:
        log(doc)
        # id = declarative_memory.add_texts( # TODO: search in uploaded documents!
        #     [doc],
        #     [{
        #         'source' : 'file.filename',
        #         'when': time.time(),
        #         'text': doc,
        #     }]
        # )
        # log(f'Inserted into memory:\n{doc}')
        # time.sleep(0.3)


    # TODO: HyDE embed    

    # reply to client
    # TODO: reply first, and then embed docs async
    return {
        'filename': file.filename,
        'content-type': file.content_type,
    }
        