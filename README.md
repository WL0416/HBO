# HBO
Search Command Format
python search.py -BM25 -q <query-label> -n <num-results> -l <lexicon> -i <invlists> -m <map> [-s <stoplist>] <queryterm-1> [<queryterm-2> ... <queryterm-N>]'
Example:
python search.py -BM25 -q 401 -n 20 -l lexicon -i invlists -m map -s stoplist april unbecoming voyo chrisman

MMR (Maximum Margin Relevance) Algorithm
*** Note ***
R - All Relevant Doc Set (20)
S - Current Result Set (Insert one by one in correct order)
Di - Doc i, Dj - Doc j, Q - Query
Sim1 - similarity function 1 ( BM25)
Sim2 - Similarity function 2 (Simple pairwise doc vector similarity between (D1, D2)

MMR {
    R = [20 Relevance Result]
    S = []
    DocMax = R.Pop()
    S.Push(DocMax)

    While (R.size != 0 && S.size < Threshold)
    {
        Foreach(Di in R)
        {
            Sim1 = BM25(Di , Q)
            Sim2Max = 0 ??? Or -infinite
            Foreach (Dj in S) {
                Sim2 = Sim2(Di, Dj);
                Sim2Max = sys.max(Sim2Max, Sim2)
            }
            MMR_Di = 0.7 * Sim1 - (1 - 0.7) * Sim2Max
        }
        Get Di with Max(MMR_Di) value
        currentDoc = R.Pop(Di)
        S.Push(Di)
    }
}

