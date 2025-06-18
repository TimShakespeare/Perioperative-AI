import os
import re
import docx
import pdfplumber
import pandas as pd
import argparse
from datetime import datetime

def clean_text(s):
    """统一清洗文本"""
    if s is None:
        return ''
    return s.replace('\n', ' ').replace('\r', ' ').strip()

def extract_qa_from_text(paragraphs):
    qa_pairs = []
    question = None
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue

        # ① 标准 问/问题 提取
        if para.startswith(('问题', '问')):
            question = re.sub(r'^(问题|问)[：:]*', '', para).strip()
            if i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1].strip()
                if next_para.startswith(('回答', '答')):
                    answer = re.sub(r'^(回答|答)[：:]*', '', next_para).strip()
                else:
                    answer = next_para.strip()
                qa_pairs.append({'question': clean_text(question), 'answer': clean_text(answer)})
            else:
                qa_pairs.append({'question': clean_text(question), 'answer': ''})

        # ② 编号型问句
        elif re.match(r'^\s*\d+[\.．、]?\s*(.*?)[？?]\s*$', para):
            numbered_match = re.match(r'^\s*\d+[\.．、]?\s*(.*?)[？?]\s*$', para)
            question = numbered_match.group(1).strip() + '？'
            if i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1].strip()
                if next_para.startswith(('回答', '答')):
                    answer = re.sub(r'^(回答|答)[：:]*', '', next_para).strip()
                else:
                    answer = next_para.strip()
                qa_pairs.append({'question': clean_text(question), 'answer': clean_text(answer)})
            else:
                qa_pairs.append({'question': clean_text(question), 'answer': ''})

        # ③ 兜底问号句
        elif '?' in para or '？' in para:
            question_candidate = para
            if not any(question_candidate in item['question'] for item in qa_pairs):
                if i + 1 < len(paragraphs):
                    next_para = paragraphs[i + 1].strip()
                    if next_para.startswith(('回答', '答')):
                        answer = re.sub(r'^(回答|答)[：:]*', '', next_para).strip()
                    else:
                        answer = next_para.strip()
                    qa_pairs.append({'question': clean_text(question_candidate), 'answer': clean_text(answer)})
                else:
                    qa_pairs.append({'question': clean_text(question_candidate), 'answer': ''})

    return qa_pairs

def extract_qa_from_docx(file_path):
    doc = docx.Document(file_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return extract_qa_from_text(paragraphs)

def extract_qa_from_pdf(file_path):
    paragraphs = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # 以换行切分段落
                paras = text.split('\n')
                paragraphs.extend(paras)
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    return extract_qa_from_text(paragraphs)

def batch_process(input_folder, output_file='cleaned_output.csv'):
    data = []
    total_files = 0

    for file in os.listdir(input_folder):
        if file.endswith('.docx') or file.endswith('.pdf'):
            file_path = os.path.join(input_folder, file)

            if file.endswith('.docx'):
                qa_pairs = extract_qa_from_docx(file_path)
            elif file.endswith('.pdf'):
                qa_pairs = extract_qa_from_pdf(file_path)
            else:
                qa_pairs = []

            for pair in qa_pairs:
                pair['source_file'] = file
                data.append(pair)
            total_files += 1
            print(f"✅ 已处理文件: {file}（累计 {total_files} 个文件）")

    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n🎯 清洗完成，共处理 {total_files} 个文件，共提取 {len(df)} 条问答，保存至 {output_file}")
    else:
        print("⚠ 未提取到任何问答数据，请检查源文件格式。")

def main():
    parser = argparse.ArgumentParser(description="支持docx+pdf的问答清洗器")
    parser.add_argument('--input_folder', type=str, required=True, help="包含文件的文件夹路径")
    parser.add_argument('--output_file', type=str, default=None, help="输出 CSV 文件名")
    args = parser.parse_args()

    if not args.output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output_file = f"cleaned_output_{timestamp}.csv"

    if not os.path.exists(args.input_folder):
        print(f"❌ 输入文件夹不存在: {args.input_folder}")
        return

    batch_process(args.input_folder, args.output_file)

if __name__ == '__main__':
    main()
