import datetime
import json
import arxiv
import os

def get_authors(authors, first_author=False):
    return authors[0] if first_author else ", ".join(str(author) for author in authors)

def sort_papers(papers):
    return dict(sorted(papers.items(), key=lambda item: item[0], reverse=True))

def get_weekly_papers(topic, query, max_results=2):
    """
    @param topic: str
    @param query: str
    @return paper_with_code: dict
    """
    content = {}
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)  # 一周前的日期
    # Construct the default API client.
    client = arxiv.Client()
    search_engine = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    for result in client.results(search_engine):
        publish_time = result.published.date()
        
        # 只处理最近一周内发布的文章
        if publish_time < one_week_ago.date():
            continue

        paper_id = result.get_short_id()
        paper_title = result.title
        paper_url = result.entry_id
        paper_first_author = get_authors(result.authors, first_author=True)

        print(f"Time = {publish_time}, title = {paper_title}, author = {paper_first_author}")

        paper_key = paper_id.split('v')[0]  # 取版本前的部分
        content[paper_key] = f"|**{publish_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|\n"

    return {topic: content}

def update_json_file(filename, data_all):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            json_data = json.load(f)
    else:
        json_data = {}

    for data in data_all:
        for keyword, papers in data.items():
            json_data.setdefault(keyword, {}).update(papers)

    with open(filename, "w") as f:
        json.dump(json_data, f)

def json_to_md(filename):
    """
    @param filename: str
    @return None
    """
    DateNow = datetime.date.today().strftime('%Y.%m.%d')
    md_filename = "README.md"
    archive_filename = f"README_{DateNow}.md"

    if os.path.exists(md_filename):
        os.rename(md_filename, archive_filename)

    with open(md_filename, "w") as f:
        f.write("")  # 清空文件内容

    with open(filename, "r") as f:
        data = json.load(f)

    with open(md_filename, "a") as f:
        f.write(f"## Updated on {DateNow}\n\n")
        
        for keyword, day_content in data.items():
            if day_content:
                f.write(f"## {keyword}\n\n")
                f.write("|Publish Date|Title|Authors|PDF|\n|---|---|---|---|\n")
                day_content = sort_papers(day_content)
                
                for v in day_content.values():
                    if v is not None:
                        f.write(v)

                f.write("\n")
    print("finished")     

if __name__ == "__main__":
    data_collector = []
    keywords = {
        "energy trading": "(ti:intraday AND ((ti:energy) OR (ti:power))) OR (ti:trading AND ((ti:energy) OR (ti:power))) OR (ti:bidding AND ((ti:energy) OR (ti:power)))"
    }

    for topic, keyword in keywords.items():
        print(f"Keyword: {topic}")
        data = get_weekly_papers(topic, query=keyword, max_results=10)
        data_collector.append(data)
        print("\n")

    json_file = "weekly_update.json"
    if not os.path.exists(json_file):
        with open(json_file, 'w') as a:
            print(f"create {json_file}")

    update_json_file(json_file, data_collector)
    json_to_md(json_file)
