# (주)파인가든 홈페이지 (리뉴얼 시안)

기존 워드프레스 홈페이지(finegarden.net)를 서버 프로그램 없이 동작하는 정적 사이트로 다시 만든 것입니다.
제품과 납품사례는 `content/` 폴더의 파일로, 사진은 `uploads/` 폴더에 저장됩니다.

## 제품·사례 올리는 방법 (직원용)

1. https://app.pagescms.org 에 접속해 로그인합니다.
   - GitHub 계정이 없는 직원은 저장소 관리자가 **이메일로 초대**(Pages CMS의 Collaborators)하면 그 이메일로 로그인할 수 있습니다.
2. `fine_re` 저장소를 엽니다. 왼쪽에 **제품**, **납품사례** 메뉴가 나옵니다.
3. **Add an entry**(새로 추가)를 누르고 입력한 뒤 **Save**를 누릅니다.
   - 제품: 제품명(코드), 대분류, 세부 분류, 대표 사진, 크기, 소재, 설명
   - 납품사례: 납품처, 구분, 납품 품목, 납품일, 대표 사진, 내용
   - 사진은 휴대폰 원본 그대로 올려도 됩니다. 저장 후 **긴 변 1600px 이하로 자동으로 줄여** 다시 저장합니다.
   - 제품을 잠시 내리고 싶으면 **숨기기**를 켭니다.
4. 저장하고 1~3분 뒤 홈페이지에 반영됩니다. (진행 상황: 저장소의 **Actions** 탭)

## 구조

| 경로 | 내용 |
|---|---|
| `site.yml` | 회사 정보, 메뉴, 제품 분류 설정 |
| `content/products/*.md` | 제품 (위쪽 `---` 사이에 제품명·분류·사진·크기, 그 아래 설명) |
| `content/cases/*.md` | 납품사례 |
| `uploads/` | 사진 (`products/`, `cases/`) |
| `templates/` | 페이지 디자인(HTML) |
| `css/`, `images/` | 스타일과 고정 이미지 |
| `scripts/build.py` | 파일로 사이트를 만드는 프로그램 |
| `scripts/resize_images.py` | 큰 사진 자동 축소 |
| `scripts/migrate_images.py` | 기존 사이트의 제품 사진을 한 번 옮겨 오기 (`old_image:` 가 남은 제품만) |
| `data/old_products.tsv` | 기존 사이트에서 가져온 제품 목록 원본 |
| `.pages.yml` | 글쓰기 화면(Pages CMS) 설정 |
| `.github/workflows/deploy.yml` | 저장할 때마다 사진 옮기기·축소 → 사이트 생성 → 배포 |

## 처음 설정 (한 번만)

- 저장소 **Settings → Pages → Build and deployment → Source** 를 **GitHub Actions** 로 바꿉니다.
- 자체 도메인으로 옮길 때는 `site.yml` 의 `baseurl` 을 `""` 로, `draft` 를 `false` 로 바꿉니다.
