# labs-namedmaps4js

A small script to migrate CARTO BUILDER [named map][nm] templates into [CartoDB.js v3][cdbjs] valid named map templates.

## Why

Current CARTO BUILDER maps generate [named map][nm] templates that are not compatible with [CartoDB.js v3][cdbjs]. This situation forces you to create by hand your templates which can be tedious if you have many or you update them frequently. This script aims to make easier to migrate your BUILDER maps into templates that work well with the JavaScript SDK.

Mind that this scripts assumes your maps **don't have analyses**, otherwise it will fail since that feature is not supported by CartoDB.js v3.

## How to use

* Install the `requirements.txt` using `pip`
* Copy the `namedmaps4js.conf.example` to `namedmaps4js.conf` and put your user URL and API Key
* Put in the `maps.csv` file the identifiers of your BUILDER maps web addresses that you want to migrate
* Run with `python namedmaps4js.py`

The script will create new templates with the suffix `_mod` that are ready to use from your CartoDB.js v3 applications. There is an `example.html` to see how to load this named map template and add a custom infowindow.

In any case the basic snippet is and you can see it live [here](https://rawgit.com/CartoDB/labs-namedmaps4js/master/example.html).

```js
  var namedLayerSource = {
      user_name: 'carto',
      type: 'namedmap',
      named_map: {
          name: "tpl_488f1fa4_04bf_4c35_88f9_75c0b7f66831_mod",
          layers:[
            {
              layer_name: "layer0" //states boundaries
            },
            {
              layer_name : "layer1", // trees
              interactivity: ["common_species"]
            }
          ]
      }
  };

  / add cartodb layer with one sublayer
  cartodb.createLayer(map, namedLayerSource, {
      https: true
  })
  .addTo(map)
  .done(function (layer)
    // add an infowindow for the trees sublayer
    cdb.vis.Vis.addInfowindow(
      map,
      layer.getSubLayer(1),
      ['cartodb_id','common_species'],
      {infowindowTemplate: $('#infowindow_template').html()}
    );

  })
  .error(function (err) {
      console.log("error: " + err);
  });
```


[nm]: https://carto.com/docs/carto-engine/maps-api/named-maps
[cdbjs]: https://carto.com/docs/carto-engine/maps-api/named-maps#cartojs-for-named-maps