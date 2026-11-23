/**
 * 파인가든 견적 문의 구글폼 만들기 (Google Apps Script)
 *
 * 1) https://script.google.com 에 접속 → [새 프로젝트]
 * 2) 이 파일 내용을 전부 붙여 넣고 저장 → 위쪽 [실행] (함수: createQuoteForm)
 * 3) 처음 한 번 권한 허용 창이 뜨면 허용
 * 4) 아래쪽 [실행 로그]에 나온 '폼 주소'와 '제품 칸'을 site.yml 의 quote_form.google 에 넣습니다.
 */
function createQuoteForm() {
  var form = FormApp.create('파인가든 견적 문의');
  form.setDescription(
    '설치 장소와 대략적인 크기·수량만 알려 주셔도 상담해 드립니다.\n' +
    '문의: 02-443-8272 · fine21@hanmail.net'
  );
  form.setCollectEmail(false);
  form.setConfirmationMessage('문의가 접수되었습니다. 확인 후 빠르게 연락드리겠습니다.');
  try { form.setRequireLogin(false); } catch (e) {}   // 회사(Workspace) 계정일 때만 의미 있음

  form.addTextItem().setTitle('이름 / 업체명').setRequired(true);
  form.addTextItem().setTitle('연락처').setHelpText('전화번호 또는 이메일').setRequired(true);
  var product = form.addTextItem().setTitle('원하는 제품')
    .setHelpText('예) 종합안내판, 우드라벨').setRequired(true);
  form.addParagraphTextItem().setTitle('설치 장소와 용도');
  form.addTextItem().setTitle('대략적인 크기와 수량').setHelpText('예) 600 × 200 mm, 30개');
  form.addTextItem().setTitle('희망 납기일');
  form.addParagraphTextItem().setTitle('기타 요청 사항');

  form.setAcceptingResponses(true);
  try { form.setPublished(true); } catch (e) {}       // 게시 기능이 있는 계정에서만 동작

  // 제품 칸 자동 입력용 entry 번호 알아내기
  var prefilled = form.createResponse()
    .withItemResponse(product.createResponse('X'))
    .toPrefilledUrl();
  var entry = (prefilled.match(/entry\.\d+/) || [''])[0];

  Logger.log('폼 주소: ' + form.getPublishedUrl());
  Logger.log('제품 칸: ' + entry);
  Logger.log('편집 주소: ' + form.getEditUrl());
}
