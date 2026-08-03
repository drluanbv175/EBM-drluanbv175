---
description: "Tra dược lý một thuốc: cơ chế tác dụng, đích tác động, hoạt tính sinh học, đặc tính ADMET (ChEMBL)"
---

Tra thông tin dược lý của: **$ARGUMENTS**

1. Nạp công cụ: ToolSearch với `select:mcp__plugin_bio-research_chembl__drug_search,mcp__plugin_bio-research_chembl__get_mechanism,mcp__plugin_bio-research_chembl__get_admet,mcp__plugin_bio-research_chembl__target_search`
2. Trình tự: `drug_search` tìm thuốc → `get_mechanism` xem cơ chế và đích → `get_admet` xem đặc tính dược động.
3. Trả về: hoạt chất · nhóm thuốc · cơ chế · đích tác động · chỉ định đã được duyệt.
4. Đây là CSDL nghiên cứu dược, KHÔNG phải tờ hướng dẫn sử dụng thuốc: liều dùng và chống chỉ định
   trên bệnh nhân phải tra guideline/tờ HDSD và đi qua agent `ke-don-an-toan`. **Cần bác sĩ kiểm chứng**.
